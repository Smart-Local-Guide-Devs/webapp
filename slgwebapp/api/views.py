from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import AppSerializer, SiteReviewSerializer
from .models import App

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

