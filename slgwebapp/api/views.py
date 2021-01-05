from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import AppSerializer, SiteReviewSerializer
from .models import App

# Create your views here.

@api_view(['GET'])
def search(request):
	app_name = request.GET['app_name']
	apps = App.objects.filter(app_name__icontains=app_name)
	serializer = AppSerializer(instance=apps, many=True)
	return Response(data=serializer.data)

@api_view(['GET'])
def best_apps(request, count):
	genre = request.GET['genre']
	apps = App.objects.filter(genre=genre).order_by('avg_rating')[:count]
	serializer = AppSerializer(instance=apps, many=True)
	return Response(data=serializer.data)
	
@api_view(['POST'])
def site_review(request):
	serializer = SiteReviewSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)
	return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

