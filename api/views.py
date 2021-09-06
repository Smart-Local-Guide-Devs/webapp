import json
import random
import requests
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest
from django.views.decorators.cache import cache_page
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import CreateUserForm
from .models import *
from .serializers import *


def get_ip(req):
    address = req.META.get("HTTP_X_FORWARDED_FOR")
    if address:
        ip = address.split(",")[-1].strip()
    else:
        ip = req.META.get("REMOTE_ADDR")
    return ip


def send_slack_message(channel_id: str, text: str) -> None:
    requests.post(
        "https://slack.com/api/chat.postMessage",
        data=json.dumps(
            {
                "channel": channel_id,
                "text": text,
            }
        ),
        headers={
            "Content-type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {os.environ['SLACK_OAUTH_TOKEN']}",
        },
    )


# Create your views here.


@api_view(["GET"])
def search(request: HttpRequest):
    search_query = request.GET.get("search_query", "")
    genres = request.GET.getlist("genre", [])
    installs = request.GET.get("installs", 0)
    rating = request.GET.get("rating", 0)
    ratings = request.GET.get("ratings", 0)
    reviews = request.GET.get("reviews", 0)
    order = request.GET.get("orderby", "-reviews_count")
    free = request.GET.get("free", False)
    apps = App.objects.all()
    for genre in genres:
        apps = apps.filter(genre__genre__icontains=genre)
    apps = apps.filter(
        app_name__icontains=search_query,
        min_installs__gte=installs,
        avg_rating__gte=rating,
        ratings_count__gte=ratings,
        reviews_count__gte=reviews,
    )
    if free:
        apps = apps.filter(free=True)
    apps = apps.distinct(order[1:]).order_by(order)
    apps = AppSerializer(apps[:32], many=True).data
    return Response(apps)


@api_view(["POST"])
def signup(request: HttpRequest):
    if request.user.is_authenticated:
        return Response(
            data={"message": "Already logged in!"}, status=status.HTTP_200_OK
        )
    form = CreateUserForm(request.POST)
    if form.is_valid():
        form.save()
        user = form.cleaned_data.get("username")
        messages.success(request, "Account was created for " + user)
        return Response(
            data={"message": "Account created successfully!"}, status=status.HTTP_200_OK
        )
    return Response(data={"form": form}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def signin(request: HttpRequest):
    if request.user.is_authenticated:
        return Response(
            data={"message": "Already logged in!"}, status=status.HTTP_200_OK
        )
    if request.method == "POST":
        username = request.POST.get("user")
        password = request.POST.get("pass")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(
                data={"message": "Log in successful"}, status=status.HTTP_200_OK
            )
        messages.info(request, "Username or Password is Incorrect")
    return Response(data={}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def signout(request: HttpRequest):
    logout(request)
    return Response(data={"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@cache_page(60 * 15)
def best_apps(request: HttpRequest):
    city = request.GET.get("city", "")
    res = {}
    for genre in Genre.objects.prefetch_related("apps").all():
        apps = genre.apps.order_by("-reviews_count")[:4]
        res[genre.genre] = AppSerializer(apps, many=True).data
    return Response(res)


@api_view(["GET"])
@cache_page(60 * 15)
def top_users(request: HttpRequest):
    reviews = (
        Review.objects.select_related("user")
        .annotate(up_votes=Count("up_voters"))
        .order_by("-up_votes")[:10]
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
    user_name = request.POST["user_name"]
    email_id = request.POST["email_id"]
    content = request.POST["content"]
    slack_msg = f"User: {user_name}\nEmail: {email_id}\nContent: {content}"
    send_slack_message(os.environ["SLACK_SITE_REVIEWS_CHANNEL_ID"], slack_msg)
    return Response("Review Successful")


@api_view(["GET"])
@cache_page(60 * 15)
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
@cache_page(60 * 15)
def similar_apps(request: HttpRequest, app_id: str):
    app = App.objects.prefetch_related("similar_apps").get(app_id=app_id)
    similar_apps = app.similar_apps.all()[:6]
    res = AppSerializer(similar_apps, many=True).data
    return Response(res)


@api_view(["GET", "POST"])
def app_review(request: HttpRequest, app_id: str, data: dict = None):
    """
    param:
        data: only for when this method is called in the frontend app, to help pass data without altering the original
    """
    if request.method == "GET":
        app = App.objects.get(app_id=app_id)
        reviews = app.review_set.all()[:6]
        reviews = ReviewSerializer(reviews, many=True).data
        return Response(reviews)
    res = {}
    if data is None:
        data = request.POST.copy()
    if data["username"] != request.user.username:
        res["message"] = "Please login to submit a review"
        return Response(res, status.HTTP_400_BAD_REQUEST)
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        res = serializer.data
        res["message"] = "Thanks for the review"
        return Response(res)
    res = serializer.errors
    res["message"] = "Review submission unsuccessful"
    return Response(res, status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def api_app(request: HttpRequest, app_id: str):
    # TODO remove post access
    if request.method == "GET":
        app = App.objects.get(app_id=app_id)
        app = AppSerializer(app).data
        return Response(app)
    if App.objects.filter(app_id=app_id).exists():
        return Response("App Already Exists")
    slack_msg = f"User: {request.user.username}\nRequested App ID: {app_id}"
    send_slack_message(os.environ["SLACK_NEW_APPS_CHANNEL_ID"], slack_msg)
    return Response("New App Request Successfully Sent")


@api_view(["GET", "POST"])
@cache_page(60 * 15)
def all_genres(request: HttpRequest):
    genres = Genre.objects.all()
    genres = GenreSerializer(genres, many=True).data
    genres = [genre["genre"] for genre in genres]
    return Response(genres)


@api_view(["GET", "POST"])
def app_review_queries(request: HttpRequest, app_id: str):
    # TODO remove post access
    queries = []
    app = App.objects.prefetch_related("genre_set__queries").get(app_id=app_id)
    for genre in app.genre_set.all():
        for query in genre.queries.all():
            queries.append(query)
    queries = random.sample(queries, min(len(queries), 6))
    return Response(queries)


@api_view(["POST"])
def up_vote_app(request: HttpRequest, app_id: str, pk: int):
    review = Review.objects.get(pk=pk)
    data = {}
    data["up_votes"] = review.up_voters.count()
    data["down_votes"] = review.down_voters.count()
    if request.user.is_anonymous:
        data["message"] = "Please login to up vote reviews"
        return Response(data, status.HTTP_400_BAD_REQUEST)
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
def down_vote_app(request: HttpRequest, app_id: str, pk: int):
    review = Review.objects.get(pk=pk)
    data = {}
    data["up_votes"] = review.up_voters.count()
    data["down_votes"] = review.down_voters.count()
    if request.user.is_anonymous:
        data["message"] = "Please login to down vote reviews"
        return Response(data, status.HTTP_400_BAD_REQUEST)
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
