from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage
import requests
from google_play_scraper import app, reviews, Sort


def get_api_route(request: HttpRequest):
    domain = get_current_site(request=request).domain
    return "http://" + domain + "/api"

# Create your views here.


def get_home_page_context(request: HttpRequest):
    top_users = requests.get(get_api_route(request) + "/top_users").json()
    counter = requests.get(get_api_route(request) + "/counter").json()
    best_apps = requests.get(get_api_route(request) + "/best_apps").json()
    review_form = {
        "username": "Name",
        "email_id": "Mail",
        "content": "Message",
    }
    return {
        "best_apps": best_apps,
        "counter": counter,
        "top_3_users": top_users[:3],
        "mid_7_users": top_users[3:10],
        "last_15_users": top_users[10:],
        "review_form": review_form,
        "add_app_status": "Enter playstore app link",
    }


def index(request):
    context = get_home_page_context(request)
    return render(
        request,
        "home.html",
        context,
    )


def search(request: HttpRequest):
    search_query = request.GET["search_query"]
    genre = request.GET.get("genre")
    installs = request.GET.get("installs")
    rating = request.GET.get("rating")
    page_num = request.GET.get("page", 1)
    response = requests.get(
        url=get_api_route(request) + "/search",
        params={
            "search_query": search_query,
            "genre": genre,
            # "installs": installs,
            # "rating": rating,
            "page": page_num,
        },
    )
    search_results = response.json()

    # for paging
    search_results = Paginator(search_results, 8)
    try:
        search_results = search_results.page(page_num)
    except EmptyPage:
        search_results = search_results.page(1)
    sub_url = "?search_query="+search_query + "&genre="+genre + "&page="

    return render(request, "searchResult.html", {"search_results": search_results, "sub_url": sub_url})


def search_nav(request: HttpRequest):
    search_query = request.GET["search_query"]
    response = requests.get(
        url=get_api_route(request) + "/search",
        params={"search_query": search_query},
    )
    search_results = response.json()
    return render(request, "searchResult.html", {"search_results": search_results})


def get_app(request: HttpRequest):
    app_id = request.GET["app_id"]
    similar_apps = requests.get(
        url=get_api_route(request) + "/similar_apps", params={"app_id": app_id}
    )
    context = app(app_id, "en", "in")
    context["similar_apps"] = similar_apps.json()
    context["reviews"], _ = reviews(app_id, "en", "in", Sort.NEWEST, 6)
    return render(
        request,
        "appPage.html",
        context,
    )


def site_review(request: HttpRequest):
    response = requests.post(
        url=get_api_route(request) + "/slg_site_review", data=request.POST
    )
    review_form = response.json()
    if response.status_code == 400:
        review_form["content"] = "Your response has been sent successfully"
    context = get_home_page_context(request)
    context["review_form"] = response.json()
    return render(
        request,
        "home.html",
        context,
    )


def app_review(request: HttpRequest):
    if request.method == "POST":
        response = requests.post(
            url=get_api_route(request) + "/app_review", data=request.POST
        )
        if response.status_code == 400:
            print(response.text)
        app_id = request.POST["app_id"]
    else:
        app_id = request.GET["app_id"]
    response = requests.get(
        url=get_api_route(request) + "/app_review",
        params={"app_id": app_id},
    )
    return render(
        request,
        "writeReview.html",
        response.json(),
    )


def login(request: HttpRequest):
    return render(request, "login.html")


def add_new_app(request: HttpRequest):
    app_link: str = request.POST["app_playstore_link"]
    app_id = app_link[app_link.find("id=") + 3:]
    add_app = requests.post(
        get_api_route(request) + "/add_new_app", data={"app_id": app_id}
    ).json()
    context = get_home_page_context(request)
    context["add_app_status"] = add_app["status"]
    return render(
        request,
        "home.html",
        context,
    )
