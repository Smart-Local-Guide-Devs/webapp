from api.forms import CreateUserForm
from django.contrib import messages
from api.views import best_apps as fetch_best_apps
from api.views import counter as fetch_counter
from api.views import top_users as fetch_top_users
from api.views import search as fetch_search_results
from api.views import similar_apps as fetch_similar_apps
from api.views import app_review_queries as fetch_app_review_queries
from api.views import app_details as fetch_app_details
from api.views import app_review as submit_app_review
from api.views import all_genres as fetch_all_genres
from api.views import app_reviews as fetch_app_reviews
from api.views import signin as signin_user
from api.views import signup as signup_user
from api.views import signout as signout_user
from django.core.paginator import EmptyPage, Paginator
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from google_play_scraper import Sort, app, reviews


# Create your views here.


def index(request):
    context = {}
    top_users = list(fetch_top_users(request).data.items())
    context["counter"] = fetch_counter(request).data
    context["best_apps"] = fetch_best_apps(request).data
    context["top_3_users"] = top_users[:3]
    context["mid_7_users"] = top_users[3:10]
    context["last_15_users"] = top_users[10:]
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
    context["reviews"] = fetch_app_reviews(request).data
    context["playstore_reviews"], _ = reviews(app_id, "en", "in", Sort.MOST_RELEVANT, 6)
    return render(
        request,
        "appPage.html",
        context,
    )


def app_review(request: HttpRequest):
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
        res = submit_app_review(request, req)
        context["review"] = res.data
        if res.status_code == 200:
            messages.success(request, "Review Submission Successful")
        else:
            messages.error(request, "Review Submission Failed")
    context["app"] = fetch_app_details(request).data
    context["queries"] = fetch_app_review_queries(request).data
    return render(
        request,
        "writeReview.html",
        context,
    )


def signin(request: HttpRequest):
    location = request.GET.get("next", request.META["HTTP_REFERER"])
    if request.method == "GET":
        return render(request, "signin.html", {"next": location})
    res = signin_user(request)
    if res.status_code == 400:
        res.data["next"] = location
        return render(request, "signin.html", res.data)
    for suffix in ["in", "out", "up"]:
        if "sign" + suffix in location:
            return redirect("index")
    return redirect(location)


def signup(request: HttpRequest):
    location = request.GET.get("next", request.META["HTTP_REFERER"])
    if request.method == "GET":
        return render(
            request,
            "signup.html",
            context={"form": CreateUserForm(), "next": location},
        )
    res = signup_user(request)
    if res.status_code == 400:
        # integrate with signin so that after redirection it leads to the
        # user's old page
        res.data["next"] = location
        return render(request, "signup.html", res.data)
    return redirect("front_signin")


def signout(request: HttpRequest):
    signout_user(request)
    return redirect(request.META["HTTP_REFERER"])
