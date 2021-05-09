from django.shortcuts import render, redirect
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import (
    AppSerializer,
    PlayStoreReviewSerializer,
    SlgSiteReviewSerializer,
)
from .models import App, PlayStoreReview
import random

# Create your views here.


@api_view(["GET"])
def search(request):
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
    apps = AppSerializer(apps, many=True)
    return Response(apps.data)


@api_view(["GET"])
def get_app(request):
    app_name = request.GET["app_name"]
    app = App.objects.get(app_name=app_name)
    app_review = PlayStoreReview.objects.filter(app=app)
    reviews = PlayStoreReviewSerializer(app_review, many=True)
    serializer = AppSerializer(app)
    return Response({"reviews": reviews.data, "app": serializer.data})


@api_view(["GET", "POST"])
def signup(request):
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
def signin(request):
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


def logout_user(request):
    logout(request)
    return redirect("index")


@api_view(["GET"])
def best_apps(request):
    res = {}
    for genre_dict in App.objects.values("play_store_genre").distinct():
        genre = genre_dict["play_store_genre"]
        apps = App.objects.filter(play_store_genre=genre).order_by("avg_rating")[:4]
        res[genre] = AppSerializer(apps, many=True).data
    return Response(res)


@api_view(["GET"])
def top_users(request):
    users = PlayStoreReview.objects.order_by("-up_vote_count")[:25]
    users = PlayStoreReviewSerializer(users, many=True)
    return Response(users.data)


@api_view(["POST"])
def slg_site_review(request):
    serializer = SlgSiteReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def counter(request):
    count_apps = App.objects.count()
    count_users = PlayStoreReview.objects.values("user_name").distinct().count()
    count_reviews = PlayStoreReview.objects.count()
    return Response(
        {"apps": count_apps, "users": count_users, "reviews": count_reviews}
    )


@api_view(["GET"])
def similar_apps(request):
    app_object = App.objects.get(app_id=request.GET["app_id"])
    genre = app_object.play_store_genre

    # This part can be used for tags when tags have been made
    # tags = app_object.genre_set.all()
    # tags_list = []
    # for tag in tags:
    #     tags_list.append(tag)
    # similar_apps = App.objects.filter(play_store_genre__in = tags_list)

    similar_apps = App.objects.filter(play_store_genre=genre)
    similar_apps = similar_apps.exclude(app_name=app_object.app_name)
    similar_apps = similar_apps.order_by("avg_rating")[:6]
    serializer = AppSerializer(similar_apps, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def app_review(request):
    if request.method == "GET":
        app_object = App.objects.get(app_id=request.GET["app_id"])
        genre_objects = app_object.genre_set.all()
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

        response = {
            "app_id": request.GET["app_id"],
            "app_name": app_object.app_name,
            "genre_string": genre_string[:-2],
            "queries": query_option_dict,
        }
        return Response(response)

    req = request.POST.copy()
    app = App.objects.get(app_id=req["app_id"])
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.get(username="anonymous_user")

    review = Review(app=app, user=user, content=req["app_review"], rating=req["stars"])
    review.save()

    req.pop("csrfmiddlewaretoken")
    req.pop("app_id")
    req.pop("stars")
    req.pop("app_review")

    for query, option_list in req.items():
        query_obj = Query.objects.get(query=query)
        option_obj = Option.objects.get(option=option_list[0])
        try:
            query_option_obj = QueryOption.objects.get(
                query=query_obj, option=option_obj
            )
        except QueryOption.DoesNotExist:
            query_option_obj = QueryOption()
            query_option_obj.query = query_obj
            query_option_obj.option = option_obj
            query_option_obj.save()
        review.query_options.add(query_option_obj)

    review.save()
    return Response(data={"status": "success"}, status=status.HTTP_200_OK)
