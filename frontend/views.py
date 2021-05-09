from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
import requests
from google_play_scraper import app


def get_api_route(request):
    domain = get_current_site(request=request).domain
    return "http://" + domain + "/api"


# Create your views here.
def index(request):
    top_users = requests.get(url=get_api_route(request) + "/top_users").json()
    counter = requests.get(url=get_api_route(request) + "/counter").json()
    best_apps = requests.get(url=get_api_route(request) + "/best_apps").json()
    return render(
        request,
        "home.html",
        {
            "best_apps": best_apps,
            "counter": counter,
            "top_3_users": top_users[:3],
            "mid_7_users": top_users[3:10],
            "last_15_users": top_users[10:],
        },
    )


def search(request):
    search_query = request.GET["search_query"]
    genre = request.GET.get("genre")
    installs = request.GET.get("installs")
    rating = request.GET.get("rating")
    response = requests.get(
        url=get_api_route(request) + "/search",
        params={
            "search_query": search_query,
            "genre": genre,
            "installs": installs,
            "rating": rating,
        },
    )
    search_results = response.json()
    return render(request, "searchResult.html", {"search_results": search_results})


def search_nav(request):
    search_query = request.GET["search_query"]
    response = requests.get(
        url=get_api_route(request) + "/search",
        params={"search_query": search_query},
    )
    search_results = response.json()
    return render(request, "searchResult.html", {"search_results": search_results})


def get_app(request):
    app_id = request.GET["app_id"]
    app_details = app(app_id, "en", "in")
    return render(
        request,
        "appPage.html",
        app_details,
    )


def site_review(request):
    response = requests.post(
        url=get_api_route(request) + "/slg_site_review", data=request.POST
    )
    print(response.json())
    return redirect("index")


def app_review(request):
    app_name = request.GET["app_name"]
    response = requests.get(
        url=get_api_route(request) + "/get_app", params={"app_name": app_name}
    )
    return render(request, "writeReview.html", {"app": response.json()})


def login(request):
    return render(request, "login.html")
