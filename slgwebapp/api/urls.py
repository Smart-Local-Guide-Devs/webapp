from django.urls import path
from . import views

urlpatterns = [
	path(route='search', view=views.search, name="api_search")
]