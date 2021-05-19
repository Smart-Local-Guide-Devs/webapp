import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from google_play_scraper.exceptions import NotFoundError
from google_play_scraper.features.app import app
from requests.api import request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .forms import CreateUserForm
from .models import *
from .serializers import *
from .word_weight import WordWeight
from .recommend_by_location import RecommendByLocation
from .similar_user_apps import SimilarUserApps

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
    # city = request.GET["city"]
    res = {}
    for genre in Genre.objects.prefetch_related("apps").all():
        apps = genre.apps.order_by("-reviews_count")[:6]
        res[genre.genre] = AppSerializer(apps, many=True).data
    return Response(res)


@api_view(["GET"])
@cache_page(60 * 15)
def top_users(request: HttpRequest):
    reviews = Review.objects.select_related("user").order_by("-up_votes")[:25]
    users = {}
    for review in reviews:
        if review.user.username not in users:
            users[review.user.username] = review.up_votes
    return Response(users)


@api_view(["POST"])
def slg_site_review(request: HttpRequest):
    serializer = SlgSiteReviewSerializer(data=request.POST)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def counter(request: HttpRequest):
    count_apps = App.objects.count()
    count_users = User.objects.count()
    count_reviews = Review.objects.count()
    return Response(
        {"apps": count_apps, "users": count_users, "reviews": count_reviews}
    )


@api_view(["GET"])
def similar_apps(request: HttpRequest):
    app = App.objects.get(app_id=request.GET["app_id"])
    similar_apps = app.similar_apps.all()
    res = AppSerializer(similar_apps, many=True).data
    return Response(res)


@api_view(["POST"])
def app_review(request: HttpRequest, data: dict = None):
    if data is None:
        data = request.POST.copy()
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_new_app(request: HttpRequest):
    app_id = request.POST["app_id"]
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
            return Response("app successfully added", status.HTTP_201_CREATED)
        return Response(
            "app does not satisfy required criterias", status.HTTP_400_BAD_REQUEST
        )
    except NotFoundError:
        return Response("app not found", status.HTTP_400_BAD_REQUEST)


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


def get_ip(req):
    address = req.META.get('HTTP_X_FORWARDED_FOR')
    if address:
        ip = address.split(',')[-1].strip()
    else:
        ip = req.META.get('REMOTE_ADDR')
    return ip

def get_visitors_count(req):
    # done using the count of different ips visiting the site 
    # would not give actual count but would be a rough estimate
    # for low amount of traffic the count would be pretty close
    ip = get_ip(req)
    visitor = Visitors(visitor=ip)
    result = Visitors.objects.filter(Q(visitor__icontains=ip))
    if len(result) >= 1:
        pass
    else:
        visitor.save()
    visitors_count = Visitors.objects.all().count()
    return visitors_count