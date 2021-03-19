from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
import requests


def get_api_route(request):
    domain = get_current_site(request=request).domain
    return "http://" + domain + "/api"


# Create your views here.
def index(request):
    top_users = requests.get(url=get_api_route(request) + "/top_users").json()
    counter = requests.get(url=get_api_route(request) + "/counter").json()
    best_apps = requests.get(url=get_api_route(request) + "/best_apps").json()
    print(request.GET)
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
    response = requests.get(
        url=get_api_route(request) + "/search", params={"search_query": search_query}
    )
    return render(request, "searchResult.html", {"search_results": response.json()})


def get_app(request):
    app_name = request.GET["app_name"]
    response = requests.get(
        url=get_api_route(request) + "/get_app", params={"app_name": app_name}
    ).json()
    ratings_count = response["app"]["ratings_count"]
    histogram = {
        "1_star_percent": response["app"]["one_stars"] * 100 / ratings_count,
        "2_star_percent": response["app"]["two_stars"] * 100 / ratings_count,
        "3_star_percent": response["app"]["three_stars"] * 100 / ratings_count,
        "4_star_percent": response["app"]["four_stars"] * 100 / ratings_count,
        "5_star_percent": response["app"]["five_stars"] * 100 / ratings_count,
    }
    return render(
        request,
        "appPage.html",
        {
            "app": response["app"],
            "histogram": histogram,
            "reviews": response["reviews"],
        },
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
