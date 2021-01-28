from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import AppSerializer, PlayStoreReviewSerializer
from django.contrib.auth.models import User
from .models import App, Review, PlayStoreReview

# Create your views here.

@api_view(['GET'])
def search(request):
	search_query = request.GET['search_query']
	apps = App.objects.filter(app_name__icontains=search_query)
	serializer = AppSerializer(apps, many=True)
	return Response(data=serializer.data )

@api_view(['GET'])
def get_app(request):
	app_name = request.GET['app_name']

	app = App.objects.get(app_name=app_name)
	app_id=app.id;
	app_review=PlayStoreReview.objects.filter(app=app_id)
	reviewSerializer=PlayStoreReviewSerializer(app_review,many=True)
	serializer = AppSerializer(app)
	return Response({'review':reviewSerializer.data,'apps':serializer.data})

@api_view(['GET'])
def best_apps(request):
	res = {}	
	for genre_dict in App.objects.values('play_store_genre').distinct():
		genre = genre_dict['play_store_genre']
		apps = App.objects.filter(play_store_genre=genre).order_by('avg_rating')[:4]
		res[genre] = AppSerializer(apps, many=True).data
	return Response(data=res)

@api_view()
def top_users(request):
	user = PlayStoreReview.objects.order_by('-up_vote_count')[:10]
	serializer = PlayStoreReviewSerializer(user, many=True)
	return Response(data=serializer.data)
	
@api_view(['POST'])
def slg_site_review(request):
	serializer = PlayStoreReviewSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)
	return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view()
def counter(request):
	count_apps = App.objects.count()
	count_users = PlayStoreReview.objects.values('user_name').distinct()
	count_reviews = PlayStoreReview.objects.count()
	return Response({'apps': count_apps, 'users': count_users, 'reviews': count_reviews})