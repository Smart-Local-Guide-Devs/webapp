from django.urls import path,include
from . import views
from api import views

urlpatterns = [
    
    path(route='', view=views.index, name="index"),
	path(route='product', view=views.product, name="product"),
	path(route='review', view=views.review_form, name="review_form"),
	
	path(route='search', view=views.search, name="front_search")
]