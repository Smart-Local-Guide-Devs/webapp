from django.urls import path
from . import views
from django.urls import path,include

urlpatterns = [
    
    
	path(route='search', view=views.search, name="api_search"),
	path(route='signin', view=views.signin, name="signin"),
	path(route='logout', view=views.logoutUser, name="logout"),
	path('social-auth/', include('social_django.urls', namespace="social")),
	path(route='signup', view=views.signup, name="signup"),
	
	path(route='get_app', view=views.get_app, name='api_get_app'),
	path(route='best_apps', view=views.best_apps, name="api_best_apps"),
	path(route='slg_site_review', view=views.slg_site_review, name="api_slg_site_review"),
	path(route='counter',view=views.counter, name="api_counter"),
	path(route='top_users', view=views.top_users, name="api_top_users")
]