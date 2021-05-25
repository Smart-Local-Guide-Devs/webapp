from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get_app", views.get_app, name="front_get_app"),
    path("app_review", views.app_review, name="front_app_review"),
    path("signin", views.signin, name="front_signin"),
    path("signup", views.signup, name="front_signup"),
    path("signout", views.signout, name="front_signout"),
    path("search", views.search, name="front_search"),
]
