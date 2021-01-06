from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers, status
from .serializers import AppReviewSerializer, AppSerializer, SiteReviewSerializer
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

	app = App.objects.get(app_name=request.data['app_name'])
	request.data.pop('app_name')
	request.data['app'] = app.pk
	user = User.objects.get(username=request.data['user_name'])
	request.data.pop('user_name')
	request.data['user'] = user.pk
	serializer = AppReviewSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)
	return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
