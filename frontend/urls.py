from django.urls import path
from . import views

urlpatterns = [
    path(route='', view=views.index, name="index"),
	path(route='get_app', view=views.get_app, name="front_get_app"),
	path(route='app_review', view=views.app_review, name="front_app_review"),
	path(route='login', view=views.login, name="login"),
	path(route='search', view=views.search, name="front_search"),
	path(route='site_review', view=views.site_review, name='front_site_review' ),	
]