from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from google_play_scraper.features.app import app
from google_play_scraper.exceptions import NotFoundError
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
import random
import requests
import urllib.request
import json


def get_location():
    with urllib.request.urlopen("https://geolocation-db.com/json") as url:
        data = json.loads(url.read().decode())
    return data

# Create your views here.


@api_view(["GET"])
def search(request: HttpRequest):
    search_query = request.GET["search_query"]
    genre = request.GET.get("genre")
    installs = request.GET.get("installs")
    rating = request.GET.get("rating")
    apps = App.objects.filter(app_name__icontains=search_query)
    if genre != "" and genre is not None:
        apps = apps.filter(play_store_genre__icontains=genre)
    if installs != "" and installs is not None:
        apps = apps.filter(min_installs__gte=installs)
    if rating != "" and rating is not None:
        apps = apps.filter(avg_rating__gte=rating)
    res = []
    for search_app in apps:
        res.append(app(search_app.app_id, "en", "in"))
    return Response(res)


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
    res = {}
    for genre in Genre.objects.all():
        res[genre.genre_name] = []
        for genre_app in genre.apps.order_by("avg_rating")[:4]:
            res[genre.genre_name].append(app(genre_app.app_id, "en", "in"))
    return Response(res)


@api_view(["GET"])
def top_users(request: HttpRequest):
    reviews = Review.objects.order_by("-up_votes")[:25]
    res = []
    for review in reviews:
        res.append(review.user.username)
    return Response(res)


@api_view(["POST"])
def slg_site_review(request: HttpRequest):
    serializer = SlgSiteReviewSerializer(data=request.data)
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
    app_object = App.objects.get(app_id=request.GET["app_id"])
    genre = app_object.play_store_genre

    # This part can be used for tags when tags have been made
    # tags = app_object.genre_set.all()
    # tags_list = []
    # for tag in tags:
    #     tags_list.append(tag)
    # similar_apps = App.objects.filter(play_store_genre__in = tags_list)

    similar_apps = App.objects.filter(play_store_genre=genre)
    similar_apps = similar_apps.exclude(app_id=app_object.app_id)
    similar_apps = similar_apps.order_by("avg_rating")[:6]
    res = []
    for similar_app in similar_apps:
        res.append(app(similar_app.app_id, "en", "in"))
    return Response(res)


def get_genres_and_queries(genre_objects):
    query_list = []
    genre_string = ""

    for genre_obj in genre_objects:
        genre_string += genre_obj.genre_name + ", "
        for query_obj in genre_obj.queries.all():
            if query_obj in query_list:
                continue
            query_list.append(query_obj)
    query_list = random.sample(query_list, min(len(query_list), 6))

    query_option_dict = {}
    for query_obj in query_list:
        options = []
        for option_obj in query_obj.options.all():
            options.append(option_obj.option)
        query_option_dict[query_obj.query] = options

    return genre_string, query_option_dict


@api_view(["GET", "POST"])
def app_review(request: HttpRequest):
    if request.method == "GET":
        app_object = App.objects.get(app_id=request.GET["app_id"])
        genre_objects = app_object.genre_set.all()
        genre_string, query_option_dict = get_genres_and_queries(genre_objects)
        location = get_location()
        city = location["city"]
        response = {
            "app_id": request.GET["app_id"],
            "app_name": app_object.app_name,
            "genre_string": genre_string[:-2],
            "queries": query_option_dict,
            "city": city,
        }

        return Response(response)

    location = get_location()
    city = location["city"]

    req = request.POST.copy()
    app = App.objects.get(app_id=req["app_id"])
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.get(username="anonymous_user")

    review = Review(
        app=app, user=user, content=req["app_review"], rating=req["stars"], city=city, up_votes=1
    )
    review.save()

    req.pop("csrfmiddlewaretoken")
    req.pop("app_id")
    req.pop("stars")
    req.pop("app_review")

    for query, option_list in req.items():
        query_obj = Query.objects.get(query=query)
        option_obj = Option.objects.get(option=option_list[0])
        query_option_obj, _ = QueryOption.objects.get_or_create(
            query=query_obj, option=option_obj
        )
        review.query_options.add(query_option_obj)

    review.save()
    return Response({"status": "success"}, status.HTTP_200_OK)


@api_view(["POST"])
def add_new_app(request: HttpRequest):
    app_id = request.POST["app_id"]
    try:
        new_app = app(app_id, "en", "in")
        new_app_obj = App(
            app_id=new_app["appId"],
            app_name=new_app["title"],
            app_description=new_app["description"],
            app_summary=new_app["summary"],
            play_store_genre=new_app["genre"],
            min_installs=new_app["minInstalls"],
            avg_rating=new_app["score"],
            ratings_count=new_app["ratings"],
            reviews_count=new_app["reviews"],
            one_stars=new_app["histogram"][0],
            two_stars=new_app["histogram"][1],
            three_stars=new_app["histogram"][2],
            four_stars=new_app["histogram"][3],
            five_stars=new_app["histogram"][4],
            free=new_app["free"],
        )
        new_app_obj.save()
        return Response({"status": "app successfully added"}, status.HTTP_200_OK)
    except NotFoundError:
        return Response({"status": "app not found"}, status.HTTP_400_BAD_REQUEST)
