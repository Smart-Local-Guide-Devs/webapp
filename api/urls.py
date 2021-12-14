from django.urls import path
from . import views

urlpatterns = [
    path("search", views.search, name="api_search"),
    path("signout", views.signout, name="api_signout"),
    path("app/best", views.best_apps, name="api_best_apps"),
    path("app/<str:app_id>/similar", views.similar_apps, name="api_similar_apps"),
    path("app/<str:app_id>/review", views.app_review, name="api_app_reviews"),
    path(
        "review/<int:review_pk>",
        views.delete_review,
        name="api_delete_review",
    ),
    path("feedback", views.feedback, name="api_feedback"),
    path("counter", views.counter, name="api_counter"),
    path("user/best", views.top_users, name="api_top_users"),
    path("app/genre", views.all_genres, name="api_all_genres"),
    path(
        "app/<str:app_id>/review/queries",
        views.app_review_queries,
        name="api_app_review_queries",
    ),
    path("app/<str:app_id>", views.api_app, name="api_app"),
    path(
        "app/<str:app_id>/review/<int:review_pk>/up_vote",
        views.up_vote_app,
        name="api_up_vote_app",
    ),
    path(
        "app/<str:app_id>/review/<int:review_pk>/down_vote",
        views.down_vote_app,
        name="api_down_vote_app",
    ),
    path("user/<str:username>", views.user_details, name="api_user_details"),
]
