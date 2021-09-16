from django.contrib import messages
from api.views import best_apps as fetch_best_apps
from api.views import counter as fetch_counter
from api.views import top_users as fetch_top_users
from api.views import search as fetch_search_results
from api.views import similar_apps as fetch_similar_apps
from api.views import app_review_queries as fetch_app_review_queries
from api.views import api_app as fetch_app_details
from api.views import app_review as submit_app_review
from api.views import all_genres as fetch_all_genres
from api.views import app_review as fetch_app_reviews
from api.views import signout as signout_user
from api.views import up_vote_app as upvote_review
from api.views import down_vote_app as downvote_review
from django.core.paginator import EmptyPage, Paginator
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from concurrent.futures import ThreadPoolExecutor
from google_play_scraper import Sort, app, reviews


def execute_parrallelly(*args) -> tuple:
    with ThreadPoolExecutor() as executor:
        return_futures = (
            executor.submit(args[i], *args[i + 1]) for i in range(0, len(args), 2)
        )
        return_futures = (return_future.result() for return_future in return_futures)
        return tuple(return_futures)


# Create your views here.


def index(request: HttpRequest):
    context = {}
    (
        context["top_users"],
        context["best_apps"],
        context["counter"],
    ) = execute_parrallelly(
        fetch_top_users,
        (request,),
        fetch_best_apps,
        (request,),
        fetch_counter,
        (request,),
    )
    context["counter"] = context["counter"].data
    context["best_apps"] = context["best_apps"].data
    for genre, apps in context["best_apps"].items():
        for i, app in enumerate(apps):
            context["best_apps"][genre][i]["app_name"] = app["app_name"].split()[0]
            context["best_apps"][genre][i]["avg_rating"] = round(app["avg_rating"], 2)
            if app["reviews_count"] > 1e6:
                context["best_apps"][genre][i]["reviews_count"] = (
                    str(round(app["reviews_count"] / 1e6, 1)) + " M"
                )
            elif app["reviews_count"] > 1e3:
                context["best_apps"][genre][i]["reviews_count"] = (
                    str(round(app["reviews_count"] / 1e3, 1)) + " K"
                )
    context["top_users"] = context["top_users"].data
    return render(
        request,
        "homePage.html",
        context,
    )


prev_search_query = ""
prev_search_result: Paginator


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
    res["search_genres"] = request.GET.getlist("search_genres", [])
    res["rating"] = request.GET.get("rating", 0)
    res["installs"] = request.GET.get("installs", 0)
    res["ratings"] = request.GET.get("ratings", 0)
    res["reviews"] = request.GET.get("reviews", 0)
    res["free"] = request.GET.get("free", "false")
    return render(
        request,
        "searchPage.html",
        res,
    )


def get_app(request: HttpRequest, app_id: str):
    context = app(app_id, "en", "in")
    context["score"] = round(context["score"], 2)
    context["similar_apps"] = fetch_similar_apps(request, app_id).data
    context["reviews"] = fetch_app_reviews(request, app_id).data
    context["playstore_reviews"], _ = reviews(app_id, "en", "in", Sort.MOST_RELEVANT, 6)
    return render(
        request,
        "appInfoPage.html",
        context,
    )


def app_review(request: HttpRequest, app_id: str):
    context = {}
    if request.method == "POST":
        req = request.POST.dict()
        req["username"] = request.user.username
        req["query_choices"] = []
        for key, value in req.items():
            if key.startswith("query: "):
                req["query_choices"].append(
                    {"query": key.removeprefix("query: "), "choice": value}
                )
        res = submit_app_review(request, app_id, req)
        context["review"] = res.data
        if res.status_code == 200:
            messages.success(request, "Review Submission Successful")
        else:
            messages.error(request, "Review Submission Failed")
    context["app"] = fetch_app_details(request, app_id).data
    context["queries"] = fetch_app_review_queries(request, app_id).data
    return render(
        request,
        "writeReview.html",
        context,
    )


def signout(request: HttpRequest):
    signout_user(request)
    return redirect(request.META["HTTP_REFERER"])
