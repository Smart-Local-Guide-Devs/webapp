from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("base", views.base, name="base"),
    path("app/<str:app_id>/", views.get_app, name="front_get_app"),
    path("app/<str:app_id>/review", views.app_review, name="front_app_review"),
    path("signin", views.signin, name="front_signin"),
    path("signup", views.signup, name="front_signup"),
    path("signout", views.signout, name="front_signout"),
    path("search", views.search, name="front_search"),
    path(
        "app/<str:app_id>/review/<int:pk>/up_vote",
        views.review_upvote,
        name="review_upvote",
    ),
    path(
        "app/<str:app_id>/review/<int:pk>/down_vote",
        views.review_downvote,
        name="review_downvote",
    ),
]
