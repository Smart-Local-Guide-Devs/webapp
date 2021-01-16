from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers, status
from .serializers import AppReviewSerializer, AppSerializer, SiteReviewSerializer, NewAppReviewSerializer
from .models import App, AppReview

# Create your views here.

@api_view(['GET'])
def search(request):
	search_query = request.GET['search_query']
	apps = App.objects.filter(app_name__icontains=search_query)
	serializer = AppSerializer(instance=apps, many=True)
	return Response(data=serializer.data)

@api_view(['GET'])
def get_app(request):
	app_name = request.GET['app_name']
	app = App.objects.get(app_name=app_name)
	serializer = AppSerializer(instance=app)
	return Response(data=serializer.data)

@api_view(['GET'])
def best_apps(request):
	res = {}	
	for genre_dict in App.objects.values('genre').distinct():
		genre = genre_dict['genre']
		apps = App.objects.filter(genre=genre).order_by('avg_rating')[:4]
		res[genre] = AppSerializer(instance=apps, many=True).data
	return Response(data=res)
	
@api_view(['POST'])
def site_review(request):
	serializer = SiteReviewSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)
	return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def app_review(request):
	if (request.method == 'GET'):
		res = {}	
		for genre_dict in App.objects.values('genre').distinct():
			genre = genre_dict['genre']
			res[genre] = {f'{genre[:5]}_query_{i}': [f'{genre[:5]}_query_{i}_choice_{j}' for j in range(4)] for i in range(4)}
		return Response(data=res)

	mutable = request.data.copy()
	app_found = False
	if(App.objects.filter(app_name=mutable['app_name']).count() != 0):
		app = App.objects.get(app_name=mutable['app_name'])
		mutable['app'] = app.pk
		app_found = True

	else:
		app = mutable['app_name']
		mutable['app'] = app
	
	mutable.pop('app_name')
	review = mutable['app_review']
	mutable.pop('app_review')
	mutable['review'] = review
	# temporary arrangement till availablility of genre queries
	for i in range(4):
		mutable.pop(f'TRAVE_query_{i}')
		
	if(app_found):
		serializer = AppReviewSerializer(data=mutable)
	else:
		serializer = NewAppReviewSerializer(data=mutable)
	 # case : if user is not authenticated and if he/she is
	 # case : genre queries
	
	if serializer.is_valid():
		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)
	return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
