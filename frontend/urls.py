from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("app/<str:app_id>/", views.get_app, name="front_get_app"),
    path("signout", views.signout, name="front_signout"),
    path("search", views.search, name="front_search"),
    path("user/<str:username>", views.user_details, name="front_user"),
]
