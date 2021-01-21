from django.urls import path
from . import views

urlpatterns = [
	path(route='search', view=views.search, name="api_search"),
	path(route='get_app', view=views.get_app, name='api_get_app'),
	path(route='best_apps', view=views.best_apps, name="api_best_apps"),
	path(route='site_review', view=views.site_review, name="api_site_review"),
	path(route='count',view=views.counter, name="api_counter")
]