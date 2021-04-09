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
    if request.method == 'GET':
        app_object = App.objects.get(app_name=request.GET['app_name'])
        genre_objects = app_object.genre_set.all()
        query_list = []

        for genre_obj in genre_objects:
            for query_obj in genre_obj.queries.all():
                if query_obj in query_list:
                    continue
                query_list.append(query_obj)
        query_list = random.sample(query_list, min(len(query_list), 6))

        response = {}
        for query_obj in query_list:
            temp = []
            for option_obj in query_obj.options.all():
                temp.append(option_obj.option) 
            response[query_obj.query] = temp

        # adding temporary fix for genre issue
        res = {'Travel and Tourism' : response, 'Food' : response, 'Air travel' : response}
        return Response(data=res)
        #return Response(data=response)

    req = request.POST.copy()
    app = App.objects.get(app_name=req['app_name'])
    genre = Genre.objects.get(genre_name=req['genre'])
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.get(username='anonymous_user')

    req.pop('csrfmiddlewaretoken')
    req.pop('app_name')
    req.pop('genre')
    req.pop('stars')
    req.pop('app_review')

    review = Review(app=app, user=user, content=req['content'], rating=req['rating'], genre=genre)
    review.save()
    
    for query, option_list in req.items():
        query_obj = Query.objects.get(query=query)
        option_obj = Option.objects.get(option=option_list[0])
        try:
            query_option_obj = QueryOption.objects.get(query=query_obj, option=option_obj)
        except QueryOption.DoesNotExist:
            query_option_obj = QueryOption()
            query_option_obj.query = query_obj
            query_option_obj.option = option_obj
            query_option_obj.save()
        review.query_options.add(query_option_obj)

    review.save()
    return Response(data={'status' : 'success'}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def counter(request):
    count_apps = App.objects.count()
    count_users = PlayStoreReview.objects.values(
        'user_name').distinct().count()
    count_reviews = PlayStoreReview.objects.count()
    return Response({'apps': count_apps, 'users': count_users, 'reviews': count_reviews})
