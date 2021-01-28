from django.urls import path
from . import views
from django.urls import path,include

urlpatterns = [
    
    
	path(route='search', view=views.search, name="api_search"),
	path(route='signin', view=views.signin, name="signin"),
	path(route='logout', view=views.logoutUser, name="logout"),
	path('social-auth/', include('social_django.urls', namespace="social")),
	path(route='signup', view=views.signup, name="signup"),
]