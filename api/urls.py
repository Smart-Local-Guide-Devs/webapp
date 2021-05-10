from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path("search", views.search, name="api_search"),
    path("signin", views.signin, name="signin"),
    path("logout", views.logout_user, name="logout"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("signup", views.signup, name="signup"),
    path("best_apps", views.best_apps, name="api_best_apps"),
    path("similar_apps", views.similar_apps, name="similar_apps"),
    path("app_review", views.app_review, name="api_app_review"),
    path("slg_site_review", views.slg_site_review, name="api_slg_site_review"),
    path("counter", views.counter, name="api_counter"),
    path("top_users", views.top_users, name="api_top_users"),
    path("add_new_app", views.add_new_app, name="api_add_new_app"),
]
