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
from .serializers import *


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
    apps = apps.filter(genre__genre_name__icontains=genre)
    apps = apps.filter(app_name__icontains=search_query)
    apps = apps.filter(min_installs__gte=installs)
    apps = apps.filter(avg_rating__gte=rating)
    apps = apps.filter(ratings_count__gte=ratings)
    apps = apps.filter(reviews_count__gte=reviews)
    if free:
        apps = apps.filter(free=True)
    apps.order_by("reviews_count")
    res = []
    for search_app in apps[:32]:
        try:
            res.append(app(search_app.app_id, "en", "in"))
        except NotFoundError:
            pass
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
@cache_page(60 * 15)
def best_apps(request: HttpRequest):
    res = {}
    for genre in Genre.objects.prefetch_related("apps").all():
        res[genre.genre_name] = []
        for genre_app in genre.apps.order_by("reviews_count")[:4]:
            try:
                res[genre.genre_name].append(app(genre_app.app_id, "en", "in"))
            except NotFoundError:
                pass
    return Response(res)


@api_view(["GET"])
@cache_page(60 * 15)
def top_users(request: HttpRequest):
    reviews = Review.objects.select_related("user").order_by("-up_votes")[:25]
    res = {}
    for review in reviews:
        res[review.user.username] = max(
            review.up_votes, res.get(review.user.username, 1)
        )
    return Response(res)


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
    app_object = App.objects.get(app_id=request.GET["app_id"])
    genre = app_object.play_store_genre

    # This part can be used for tags when tags have been made
    # tags = app_object.genre_set.all()
    # tags_list = []
    # for tag in tags:
    #     tags_list.append(tag.genre_name)
    # similar_apps = App.objects.filter(play_store_genre__in = tags_list)

    similar_apps = App.objects.filter(play_store_genre=genre)
    similar_apps = similar_apps.exclude(app_id=app_object.app_id)
    similar_apps = similar_apps.order_by("avg_rating")[:6]
    res = []
    for similar_app in similar_apps:
        try:
            res.append(app(similar_app.app_id, "en", "in"))
        except NotFoundError:
            pass
    return Response(res)


@api_view(["POST"])
def app_review(request: HttpRequest):

    req = request.POST.copy()
    app = App.objects.get(app_id=req["app_id"])
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.get(username="anonymous_user")

    review = Review(
        app=app,
        user=user,
        content=req["app_review"],
        rating=req["stars"],
        city=req["city"],
        up_votes=1,
    )
    review.save()

    req.pop("csrfmiddlewaretoken")
    req.pop("app_id")
    req.pop("stars")
    req.pop("app_review")
    req.pop("city")

    for query, option in req.items():
        query_obj = Query.objects.get(query=query)
        option_obj = Option.objects.get(option=option)
        query_option_obj, _ = QueryOption.objects.get_or_create(
            query=query_obj, option=option_obj
        )
        review.query_options.add(query_option_obj)


    # for alert message on submission of review
    
    # if req.is_valid():
    #     messages.success(request, 'Review submission successful')

    review.save()
    return Response("review successfully submitted", status.HTTP_201_CREATED)


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
        return Response({"status": "app successfully added"}, status.HTTP_201_CREATED)
    except NotFoundError:
        return Response({"status": "app not found"}, status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@cache_page(60 * 15)
def all_genres(request: HttpRequest):
    genres = Genre.objects.all()
    res = []
    for genre in genres:
        res.append(genre.genre_name)
    return Response(res)


@api_view(["GET"])
def app_review_queries(request: HttpRequest):
    res = {}
    queries = []
    app_id = request.GET["app_id"]
    app_obj = App.objects.get(app_id=app_id)
    for genre in app_obj.genre_set.prefetch_related("queries").all():
        for query in genre.queries.prefetch_related("options").all():
            queries.append(query)
    queries = random.sample(queries, min(len(queries), 6))
    for query in queries:
        res[query.query] = []
        for option in query.options.all():
            res[query.query].append(option.option)
    return Response(res)


@api_view(["GET"])
def app_details(request: HttpRequest):
    app_id = request.GET["app_id"]
    app_obj = App.objects.prefetch_related("genre_set").get(app_id=app_id)
    res = AppSerializer(app_obj).data
    res["genres"] = []
    for genre in app_obj.genre_set.all():
        res["genres"].append(genre.genre_name)
    return Response(res)
