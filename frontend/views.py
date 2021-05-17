import requests
from api.views import best_apps as fetch_best_apps
from api.views import counter as fetch_counter
from api.views import top_users as fetch_top_users
from api.views import search as fetch_search_results
from api.views import similar_apps as fetch_similar_apps
from api.views import slg_site_review as submit_slg_site_review
from api.views import app_review_queries as fetch_app_review_queries
from api.views import app_details as fetch_app_details
from api.views import app_review as submit_app_review
from api.views import all_genres as fetch_all_genres
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import EmptyPage, Paginator
from django.http.request import HttpRequest
from django.shortcuts import render
from google_play_scraper import Sort, app, reviews


def get_user_city():
    return requests.get("https://geolocation-db.com/json").json()["city"]


def get_api_route(request: HttpRequest):
    domain = get_current_site(request=request).domain
    return "http://" + domain + "/api"


def get_home_page_context(req: HttpRequest):
    method = req.method
    req.method = "GET"
    top_users = list(fetch_top_users(req).data.items())
    counter = fetch_counter(req).data
    best_apps = fetch_best_apps(req).data
    review_form = {
        "username": "Name",
        "email_id": "Mail",
        "content": "Message",
    }
    req.method = method
    return {
        "best_apps": best_apps,
        "counter": counter,
        "top_3_users": top_users[:3],
        "mid_7_users": top_users[3:10],
        "last_15_users": top_users[10:],
        "review_form": review_form,
        "add_app_status": "Enter playstore app link",
        "genres": best_apps.keys(),
        "location": get_user_city(),
    }


# Create your views here.


def index(request):
    context = get_home_page_context(request)
    return render(
        request,
        "home.html",
        context,
    )


prev_search_query = ""
prev_search_result = {}


def search(request: HttpRequest):
    res = {}
    sub_url = request.get_full_path(False)
    idx = sub_url.find("page=")
    if idx >= 0:
        sub_url = sub_url[: idx - 1]
    global prev_search_query, prev_search_result
    if prev_search_query != sub_url:
        prev_search_query = sub_url
        prev_search_result = fetch_search_results(request).data
        prev_search_result = Paginator(prev_search_result, 8)
    search_results = prev_search_result
    page_num = request.GET.get("page", 1)
    # for paging
    try:
        search_results = search_results.page(page_num)
    except EmptyPage:
        search_results = search_results.page(1)
    sub_url += "&page="
    res["search_results"] = search_results
    res["sub_url"] = sub_url
    res["genres"] = fetch_all_genres(request).data
    res["add_app_status"] = "Enter playstore app link"
    res["search_query"] = request.GET.get("search_query", "")
    res["genre"] = request.GET.get("genre", "")
    res["rating"] = request.GET.get("rating", 0)
    res["installs"] = request.GET.get("installs", 0)
    res["ratings"] = request.GET.get("ratings", 0)
    res["reviews"] = request.GET.get("reviews", 0)
    res["free"] = request.GET.get("free", "false")
    return render(
        request,
        "searchResult.html",
        res,
    )


def get_app(request: HttpRequest):
    app_id = request.GET["app_id"]
    context = app(app_id, "en", "in")
    context["similar_apps"] = fetch_similar_apps(request).data
    context["reviews"], _ = reviews(app_id, "en", "in", Sort.NEWEST, 6)
    context["genres"] = fetch_all_genres(request).data
    return render(
        request,
        "appPage.html",
        context,
    )


def site_review(request: HttpRequest):
    context = get_home_page_context(request)
    if request.method == "POST":
        response = submit_slg_site_review(request)
        context["review_form"] = response.json()
    return render(
        request,
        "home.html",
        context,
    )


def app_review(request: HttpRequest):
    res = {}
    res["review"] = "How was your experience ..."
    if request.method == "POST":
        res["review"] = submit_app_review(request).data
    res["app"] = fetch_app_details(request).data
    res["queries"] = fetch_app_review_queries(request).data
    res["genres"] = fetch_all_genres(request).data
    print(res)
    return render(
        request,
        "writeReview.html",
        res,
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
