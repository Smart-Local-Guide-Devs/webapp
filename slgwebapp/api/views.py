from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import status
from .serializers import *
from .models import *
import random

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
    app_review = PlayStoreReview.objects.filter(app=app)
    reviews = PlayStoreReviewSerializer(app_review, many=True)
    serializer = AppSerializer(app)
    return Response({'reviews': reviews.data, 'app': serializer.data})


@api_view(['GET'])
def best_apps(request):
    res = {}
    for genre_dict in App.objects.values('play_store_genre').distinct():
        genre = genre_dict['play_store_genre']
        apps = App.objects.filter(
            play_store_genre=genre).order_by('avg_rating')[:4]
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
        #         app_name = request.GET['app_name']
        res = {}
        #         res['app_name'] = app_name

        #         app_object = App.objects.get(app_name=app_name)
        #         genre_objects = app_object.genre_set.all()
        #         query_list = []

        #         for genre_obj in genre_objects:
        #             temp = {}
        #             temp_name = {}
        #             query_objects = [genre_obj.query_1, genre_obj.query_2,
        #                              genre_obj.query_3, genre_obj.query_4]
        #             query_list.append(
        #                 [genre_obj.query_1, genre_obj.query_2, genre_obj.query_3, genre_obj.query_4])

        #         query_list = random.sample(query_list, min(6, len(query_list)))

        #         for query_obj in query_list:
        #             option_objects = [
        #                 query_obj.option_1, query_obj.option_2, query_obj.option_3, query_obj.option_4]
        #             temp[query_obj.query] = QueryOptionSerializer(
        #                 option_objects, many=True).data
        #             res[genre_obj.genre_name] = temp

        return Response(data=res)

#     # TODO : POST request handling
#     mutable = request.POST.copy()
#     temp = {}
#     temp['app_name'] = App.Objects.get(app_name=mutable['app_name'])
#     temp['genre'] = Genre.Objects.get(genre_name=mutable['genre'])
#     temp['content'] = mutable['content']
#     temp['ratings'] = mutable['ratings']


@api_view(['GET'])
def counter(request):
    count_apps = App.objects.count()
    count_users = PlayStoreReview.objects.values(
        'user_name').distinct().count()
    count_reviews = PlayStoreReview.objects.count()
    return Response({'apps': count_apps, 'users': count_users, 'reviews': count_reviews})
