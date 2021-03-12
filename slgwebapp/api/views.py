from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import status
from .serializers import *
from .models import App, PlayStoreReview, Genre, ReviewQuery

# Create your views here.

@api_view(['GET'])
def search(request):
	search_query = request.GET['search_query']
	apps = App.objects.filter(app_name__icontains=search_query)
	apps = AppSerializer(apps, many=True)
	return Response(apps.data)

@api_view(['GET'])
def get_app(request):
	app_name = request.GET['app_name']
	app = App.objects.get(app_name=app_name)
	app_review=PlayStoreReview.objects.filter(app=app)
	reviews = PlayStoreReviewSerializer(app_review,many=True)
	serializer = AppSerializer(app)
	return Response({'reviews':reviews.data,'app':serializer.data})

@api_view(['GET'])
def best_apps(request):
	res = {}	
	for genre_dict in App.objects.values('play_store_genre').distinct():
		genre = genre_dict['play_store_genre']
		apps = App.objects.filter(play_store_genre=genre).order_by('avg_rating')[:4]
		res[genre] = AppSerializer(apps, many=True).data
	return Response(res)

@api_view(['GET'])
def top_users(request):
	users = PlayStoreReview.objects.order_by('-up_vote_count')[:10]
	users = PlayStoreReviewSerializer(users, many=True)
	return Response(users.data)
	
@api_view(['POST'])
def slg_site_review(request):
	serializer = PlayStoreReviewSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status.HTTP_201_CREATED)
	return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def app_review(request):
	if (request.method == 'GET'):
		res = {}	
		# for genre_dict in App.objects.values('play_store_genre').distinct():
		# 	genre = genre_dict['play_store_genre']
		# 	res[genre] = {f'{genre[:5]}_query_{i}': [f'{genre[:5]}_query_{i}_choice_{j}' for j in range(4)] for i in range(4)}
		# return Response(data=res)

		for genre_obj in Genre.objects.all():
			genre_dict = PlayStoreGenreSerializer(genre_obj).data
			temp = {}
			for i in range(1, 5):	
				pk = genre_dict[f'query_{i}']
				query_dict = ReviewQuerySerializer(ReviewQuery.objects.get(pk=pk)).data
				obj_list = []
				for j in range(1, 5):
					pk = query_dict[f'option_{j}']
					option_dict = QueryOptionSerializer(QueryOption.objects.get(pk=pk)).data
					obj_list.append(option_dict['option'])
				temp[f'{query_dict["query"]}'] = obj_list
			res[genre_dict['genre_name']] = temp
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

@api_view(['GET'])
def counter(request):
	count_apps = App.objects.count()
	count_users = PlayStoreReview.objects.values('user_name').distinct().count()
	count_reviews = PlayStoreReview.objects.count()
	return Response({'apps': count_apps, 'users': count_users, 'reviews': count_reviews})
