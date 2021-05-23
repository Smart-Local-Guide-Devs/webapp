from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get_app", views.get_app, name="front_get_app"),
    path("app_review", views.app_review, name="front_app_review"),
    path("login", views.login, name="login"),
    path("search", views.search, name="front_search"),
    path("user_profile", views.user_profile, name="user_profile"),
]
