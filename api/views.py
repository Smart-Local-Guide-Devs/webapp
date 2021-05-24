import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from django.db.models import Count
from google_play_scraper.exceptions import NotFoundError
from google_play_scraper.features.app import app
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import CreateUserForm
from .models import *
from .serializers import *
from .word_weight import WordWeight
from .recommend_by_location import RecommendByLocation
from .similar_user_apps import SimilarUserApps


def get_ip(req):
    address = req.META.get("HTTP_X_FORWARDED_FOR")
    if address:
        ip = address.split(",")[-1].strip()
    else:
        ip = req.META.get("REMOTE_ADDR")
    return ip


# Create your views here.


@api_view(["GET"])
def search(request: HttpRequest):
    search_query = request.GET.get("search_query", "").lower()
    genre = request.GET.get("genre", "")
    installs = request.GET.get("installs", 0)
    rating = request.GET.get("rating", 0)
    ratings = request.GET.get("ratings", 0)
    reviews = request.GET.get("reviews", 0)
    free = request.GET.get("free", False)
    apps = App.objects.all()
    apps = apps.filter(genre__genre__icontains=genre)
    apps = apps.filter(app_name__icontains=search_query)
    apps = apps.filter(min_installs__gte=installs)
    apps = apps.filter(avg_rating__gte=rating)
    apps = apps.filter(ratings_count__gte=ratings)
    apps = apps.filter(reviews_count__gte=reviews)
    if free:
        apps = apps.filter(free=True)
    apps.order_by("-reviews_count")
    apps = AppSerializer(apps[:32], many=True).data
    return Response(apps)


@api_view(["GET", "POST"])
def signup(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(request, "Account was created for " + user)
                return redirect("signin")
        context = {"form": form}
        return render(request, "signup.html", context)


@api_view(["GET", "POST"])
def signin(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        if request.method == "POST":
            username = request.POST.get("user")
            password = request.POST.get("pass")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.info(request, "Username or Password is Incorrect")
        context = {}
        return render(request, "signin.html", context)


@api_view(["GET", "POST"])
def logout_user(request: HttpRequest):
    logout(request)
    return redirect("index")


@api_view(["GET"])
def best_apps(request: HttpRequest):
    city = request.GET.get("city", "")
    res = {}
    for genre in Genre.objects.prefetch_related("apps").all():
        apps = genre.apps.order_by("-reviews_count")[:6]
        res[genre.genre] = AppSerializer(apps, many=True).data
    return Response(res)


@api_view(["GET"])
@cache_page(60 * 15)
def top_users(request: HttpRequest):
    reviews = (
        Review.objects.select_related("user")
        .annotate(up_votes=Count("up_voters"))
        .order_by("-up_votes")[:25]
    )
    users = {}
    for review in reviews:
        if review.user.username not in users:
            users[review.user.username] = (
                review.up_voters.count() - review.down_voters.count()
            )
    return Response(users)


@api_view(["POST"])
def slg_site_review(request: HttpRequest):
    serializer = SlgSiteReviewSerializer(data=request.POST)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def counter(request: HttpRequest):
    count_apps = App.objects.count()
    count_users = User.objects.count()
    count_reviews = Review.objects.count()
    ip = get_ip(request)
    Visitor.objects.get_or_create(ip=ip)
    count_views = Visitor.objects.count()
    return Response(
        {
            "apps": count_apps,
            "users": count_users,
            "reviews": count_reviews,
            "views": count_views,
        }
    )


@api_view(["GET"])
def similar_apps(request: HttpRequest):
    app_id = request.GET["app_id"]
    app = App.objects.prefetch_related("similar_apps").get(app_id=app_id)
    similar_apps = app.similar_apps.all()
    res = AppSerializer(similar_apps, many=True).data
    return Response(res)


@api_view(["POST"])
def app_review(request: HttpRequest, data: dict = None):
    if data is None:
        data = request.POST.copy()
    if data["username"] != request.user.username:
        return Response("Please login to submit a review", status.HTTP_400_BAD_REQUEST)
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_new_app(request: HttpRequest):
    app_id = request.POST["app_id"]
    if App.objects.filter(app_id=app_id).exists():
        return Response("App Already Exists")
    try:
        new_app = app(app_id, "en", "in")
        genres = WordWeight.get_app_genres(new_app["description"])
        if genres:
            new_app_obj = App(
                app_id=new_app["appId"],
                app_name=new_app["title"],
                app_summary=new_app["summary"],
                min_installs=new_app["minInstalls"],
                avg_rating=new_app["score"],
                ratings_count=new_app["ratings"],
                reviews_count=new_app["reviews"],
                free=new_app["free"],
                icon_link=new_app["icon"],
            )
            new_app_obj.save()
            for genre in genres:
                Genre.objects.get(genre=genre).apps.add(new_app_obj)
            return Response("Congratulations, App Successfully Added")
        return Response(
            "Unfortunately, The App Does Not Satisfy Required Criterias",
            status.HTTP_400_BAD_REQUEST,
        )
    except NotFoundError:
        return Response("Unfortunately, App Not Found", status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@cache_page(60 * 15)
def all_genres(request: HttpRequest):
    genres = Genre.objects.all()
    genres = GenreSerializer(genres, many=True).data
    genres = [genre["genre"] for genre in genres]
    return Response(genres)


@api_view(["GET", "POST"])
def app_review_queries(request: HttpRequest):
    queries = []
    app_id = (
        request.POST["app_id"] if request.method == "POST" else request.GET["app_id"]
    )
    app = App.objects.prefetch_related("genre_set__queries").get(app_id=app_id)
    for genre in app.genre_set.all():
        for query in genre.queries.all():
            queries.append(query)
    queries = random.sample(queries, min(len(queries), 6))
    return Response(queries)


@api_view(["GET", "POST"])
def app_details(request: HttpRequest):
    app_id = (
        request.POST["app_id"] if request.method == "POST" else request.GET["app_id"]
    )
    app = App.objects.get(app_id=app_id)
    app = AppSerializer(app).data
    return Response(app)


@api_view(["GET"])
def app_reviews(request: HttpRequest):
    app_id = request.GET["app_id"]
    app = App.objects.get(app_id=app_id)
    reviews = app.review_set.all()[:6]
    reviews = ReviewSerializer(reviews, many=True).data
    return Response(reviews)


@api_view(["POST"])
def up_vote_app(request: HttpRequest):
    if request.user.is_anonymous:
        return Response("Please login to up vote reviews", status.HTTP_400_BAD_REQUEST)
    app_id = request.POST["app_id"]
    username = request.POST["username"]
    app = App.objects.get(app_id=app_id)
    user = User.objects.get(username=username)
    review = Review.objects.get(app=app, user=user)
    data = {}
    data["up_votes"] = review.up_voters.count()
    data["down_votes"] = review.down_voters.count()
    if review.up_voters.filter(username=request.user.username).exists():
        data["message"] = "Already up voted once"
        return Response(data, status.HTTP_400_BAD_REQUEST)
    if review.down_voters.filter(username=request.user.username).exists():
        review.down_voters.remove(request.user)
        data["down_votes"] -= 1
    review.up_voters.add(request.user)
    data["up_votes"] += 1
    data["message"] = "Up vote successful"
    return Response(data)


@api_view(["POST"])
def down_vote_app(request: HttpRequest):
    if request.user.is_anonymous:
        return Response(
            "Please login to down vote reviews", status.HTTP_400_BAD_REQUEST
        )
    app_id = request.POST["app_id"]
    username = request.POST["username"]
    app = App.objects.get(app_id=app_id)
    user = User.objects.get(username=username)
    review = Review.objects.get(app=app, user=user)
    data = {}
    data["up_votes"] = review.up_voters.count()
    data["down_votes"] = review.down_voters.count()
    if review.down_voters.filter(username=request.user.username).exists():
        data["message"] = "Already down voted once"
        return Response(data, status.HTTP_400_BAD_REQUEST)
    if review.up_voters.filter(username=request.user.username).exists():
        review.up_voters.remove(request.user)
        data["up_votes"] -= 1
    review.down_voters.add(request.user)
    data["down_votes"] += 1
    data["message"] = "Down vote successful"
    return Response(data)
