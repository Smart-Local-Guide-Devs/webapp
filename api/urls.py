from django.urls import path
from . import views

urlpatterns = [
	path(route='search', view=views.search, name="api_search"),
	path(route='get_app', view=views.get_app, name='api_get_app'),
	path(route='best_apps', view=views.best_apps, name="api_best_apps"),
	path(route='slg_site_review', view=views.slg_site_review, name="api_slg_site_review"),
	path(route='counter',view=views.counter, name="api_counter"),
	path(route='top_users', view=views.top_users, name="api_top_users")
]