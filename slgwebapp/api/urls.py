from django.urls import path
from . import views

urlpatterns = [
	path(route='search', view=views.search, name="api_search"),
	path(route='best_apps', view=views.best_apps, name="api_best_apps"),
	path(route='site_review', view=views.site_review, name="api_site_review"),
]