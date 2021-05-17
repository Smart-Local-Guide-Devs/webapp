import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from google_play_scraper.exceptions import NotFoundError
from google_play_scraper.features.app import app
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import CreateUserForm
from .models import *
from .serializers import (
    AppSerializer,
    GenreSerializer,
    QuerySerializer,
    SlgSiteReviewSerializer,
)
from .word_weight import WordWeight

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
def app_review(request: HttpRequest):
    req = request.POST.dict()
    app = App.objects.get(app_id=req["app_id"])
    req.pop("app_id")
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.get(username="anonymous_user")

    review = Review(
        app=app,
        user=user,
        content=req["content"],
        rating=req["rating"],
        state=req["state"],
        country=req["country"],
        city=req["city"],
        up_votes=1,
    )
    review.save()

    req.pop("rating")
    req.pop("content")
    req.pop("country")
    req.pop("state")
    req.pop("city")

    for query, choice in req.items():
        query = Query.objects.get(query=query)
        query_choice, _ = QueryChoice.objects.get_or_create(
            query=query, choice=choice)
        review.query_choices.add(query_choice)
    # for alert message on submission of review
    if req.is_valid():
        messages.success(request, "Review submission successful")
    return Response("Review successfully submitted", status.HTTP_201_CREATED)


@api_view(["POST"])
def add_new_app(request: HttpRequest):
    app_id = request.POST["app_id"]
    try:
        new_app = app(app_id, "en", "in")
        new_app_obj = App(
            app_id=new_app["appId"],
            app_name=new_app["title"],
            app_summary=new_app["summary"],
            min_installs=new_app["minInstalls"],
            avg_rating=new_app["score"],
            ratings_count=new_app["ratings"],
            reviews_count=new_app["reviews"],
            free=new_app["free"],
        )
        new_app_obj.save()
        return Response("app successfully added", status.HTTP_201_CREATED)
    except NotFoundError:
        return Response("app not found", status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@cache_page(60 * 15)
def all_genres(request: HttpRequest):
    genres = Genre.objects.all()
    genres = GenreSerializer(genres, many=True).data
    genres = [genre["genre"] for genre in genres]
    return Response(genres)


@api_view(["GET"])
def app_review_queries(request: HttpRequest):
    queries = []
    app_id = request.GET["app_id"]
    app = App.objects.prefetch_related("genre_set__queries").get(app_id=app_id)
    for genre in app.genre_set.all():
        for query in genre.queries.all():
            queries.append(query)
    queries = random.sample(queries, min(len(queries), 6))
    return Response(queries)


@api_view(["GET"])
def app_details(request: HttpRequest):
    app_id = request.GET["app_id"]
    app = App.objects.get(app_id=app_id)
    app = AppSerializer(app).data
    return Response(app)
