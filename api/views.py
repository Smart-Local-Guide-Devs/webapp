import json
import random
import requests
import os

from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.views.decorators.cache import cache_page
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    search_genres = request.GET.getlist("search_genres", [])
    installs = request.GET.get("installs", 0)
    rating = request.GET.get("rating", 0)
    ratings = request.GET.get("ratings", 0)
    reviews = request.GET.get("reviews", 0)
    order = request.GET.get("orderby", "-reviews_count")
    free = request.GET.get("free", False)
    apps = App.objects.all()
    for search_genre in search_genres:
        apps = apps.filter(genre__genre__icontains=search_genre)
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


@api_view(["GET", "POST"])
def signout(request: HttpRequest):
    logout(request)
    return Response(data={"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@cache_page(60 * 15)
def best_apps(request: HttpRequest):
    city = request.GET.get("city", "")
    res = {}
    genres = {"Weather", "Business", "Map", "News"}
    for genre in Genre.objects.exclude(genre__in=genres).prefetch_related("apps").all():
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
            if len(users) > 2:
                break
    return Response(users)


@api_view(["POST"])
def feedback(request: HttpRequest):
    user_name = request.POST["user_name"]
    email_id = request.POST["email_id"]
    content = request.POST["content"]
    slack_msg = f"User: {user_name}\nEmail: {email_id}\nContent: {content}"
    send_slack_message(os.environ["SLACK_SITE_REVIEWS_CHANNEL_ID"], slack_msg)
    return Response({"message": "Feedback sent successfully"})


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
    res = {}
    apps = App.objects.prefetch_related("similar_apps").filter(app_id=app_id)
    if not apps.exists():
        res["message"] = "App not found"
        return Response(res, status.HTTP_404_NOT_FOUND)
    app = apps.first()
    similar_apps = app.similar_apps.all()[:6]
    res = AppSerializer(similar_apps, many=True).data
    return Response(res)


@api_view(["GET", "POST"])
def app_review(request: HttpRequest, app_id: str):
    res = {}
    apps = App.objects.filter(app_id=app_id)
    if not apps.exists():
        res["message"] = "App not found"
        return Response(res, status.HTTP_404_NOT_FOUND)
    app = apps.first()
    if request.method == "GET":
        reviews = app.review_set.all()[:6]
        reviews = ReviewSerializer(reviews, many=True).data
        return Response(reviews)
    if not request.user.is_authenticated:
        res["message"] = "Please login to submit a review"
        return Response(res, status.HTTP_401_UNAUTHORIZED)
    data = request.POST.dict()
    data["username"] = request.user.username
    data["query_choices"] = json.loads(data["query_choices"])
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        res = serializer.data
        res["message"] = "Thanks for the review"
        return Response(res)
    res = serializer.errors
    res["message"] = "Review submission unsuccessful"
    return Response(res, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def delete_review(request: HttpRequest, review_pk: int):
    res = {}
    if not request.user.is_authenticated:
        res["message"] = "Please login to delete a review"
        return Response(res, status.HTTP_401_UNAUTHORIZED)
    reviews = Review.objects.filter(pk=review_pk)
    if not reviews.exists():
        res["message"] = "Review not found"
        return Response(res, status.HTTP_400_BAD_REQUEST)
    review = reviews.first()
    if review.user.username != request.user.username:
        res["message"] = "You can only delete your own reviews"
        return Response(res, status.HTTP_401_UNAUTHORIZED)
    review.delete()
    res["message"] = "Review deleted successfully"
    return Response(res)


@api_view(["GET", "POST"])
def api_app(request: HttpRequest, app_id: str):
    res = {}
    if request.method == "GET":
        apps = App.objects.prefetch_related("similar_apps").filter(app_id=app_id)
        if not apps.exists():
            res["message"] = "App not found"
            return Response(res, status.HTTP_400_BAD_REQUEST)
        app = apps.first()
        app = AppSerializer(app).data
        return Response(app)
    if App.objects.filter(app_id=app_id).exists():
        res["message"] = "App Already Exists"
        return Response(res, status.HTTP_208_ALREADY_REPORTED)
    slack_msg = f"User: {request.user.username}\nRequested App ID: {app_id}"
    send_slack_message(os.environ["SLACK_NEW_APPS_CHANNEL_ID"], slack_msg)
    res["message"] = "New App Request Successfully Sent"
    return Response(res)


@api_view(["GET"])
@cache_page(60 * 15)
def all_genres(request: HttpRequest):
    genres = Genre.objects.all()
    genres = GenreSerializer(genres, many=True).data
    genres = [genre["genre"] for genre in genres]
    return Response(genres)


@api_view(["GET"])
def app_review_queries(request: HttpRequest, app_id: str):
    queries = []
    app = App.objects.prefetch_related("genre_set__queries").get(app_id=app_id)
    for genre in app.genre_set.all():
        for query in genre.queries.all():
            queries.append(query.query)
    queries = random.sample(queries, min(len(queries), 6))
    return Response(queries)


@api_view(["POST"])
def up_vote_review(request: HttpRequest, review_pk: int):
    res = {}
    reviews = Review.objects.filter(pk=review_pk)
    if not reviews.exists():
        res["message"] = "Review not found"
        return Response(res, status.HTTP_404_NOT_FOUND)
    review = reviews.first()
    res["up_votes"] = review.up_voters.count()
    res["down_votes"] = review.down_voters.count()
    if not request.user.is_authenticated:
        res["message"] = "Please login to up vote reviews"
        return Response(res, status.HTTP_401_UNAUTHORIZED)
    if review.up_voters.filter(username=request.user.username).exists():
        res["message"] = "Already up voted once"
        return Response(res, status.HTTP_409_CONFLICT)
    if review.down_voters.filter(username=request.user.username).exists():
        review.down_voters.remove(request.user)
        res["down_votes"] -= 1
    review.up_voters.add(request.user)
    res["up_votes"] += 1
    res["message"] = "Up vote successful"
    return Response(res)


@api_view(["POST"])
def down_vote_review(request: HttpRequest, review_pk: int):
    res = {}
    reviews = Review.objects.filter(pk=review_pk)
    if not reviews.exists():
        res["message"] = "Review not found"
        return Response(res, status.HTTP_404_NOT_FOUND)
    review = reviews.first()
    res["up_votes"] = review.up_voters.count()
    res["down_votes"] = review.down_voters.count()
    if not request.user.is_authenticated:
        res["message"] = "Please login to down vote reviews"
        return Response(res, status.HTTP_401_UNAUTHORIZED)
    if review.down_voters.filter(username=request.user.username).exists():
        res["message"] = "Already down voted once"
        return Response(res, status.HTTP_409_CONFLICT)
    if review.up_voters.filter(username=request.user.username).exists():
        review.up_voters.remove(request.user)
        res["up_votes"] -= 1
    review.down_voters.add(request.user)
    res["down_votes"] += 1
    res["message"] = "Down vote successful"
    return Response(res)


@api_view(["GET"])
def user_details(request: HttpRequest, username: str):
    res = {}
    users = User.objects.filter(username=username)
    if not users.exists():
        res["message"] = "User not found"
        return Response(res, status.HTTP_404_NOT_FOUND)
    user = users.first()
    reviews = user.review_set.all()
    res["reviews"] = ReviewSerializer(reviews, many=True).data
    return Response(res)
