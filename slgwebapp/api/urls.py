from django.urls import path
from . import views

urlpatterns = [
	path(route='search', view=views.search, name="api_search"),
	path(route='best5', view=views.best5, name="api_best5")
]