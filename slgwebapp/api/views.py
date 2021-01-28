from django.forms.models import model_to_dict
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
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
	return JsonResponse(model_to_dict(app))


def index(request):
	return render(request,'home.html')


def signup(request):
	if request.user.is_authenticated:
		return redirect ('index')
	else:	
		form=CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for '+ user)
				return redirect('signin')
		context = {'form':form}
		return render(request, 'signup.html', context)

def signin(request):
	if request.user.is_authenticated:
		return redirect ('index')
	else:	
		if request.method == 'POST':
			username=request.POST.get('user')
			password=request.POST.get('pass')
			user = authenticate(request,username=username,password=password)
			if user is not None:
				login(request,user)
				return redirect('index')
			else:
				messages.info(request, 'Username or Password is Incorrect')	
		context = {}
		return render(request, 'signin.html',context)	


def logoutUser(request):
	logout(request)
	return redirect('index') 				


def search(request):
    app_name = request.GET["app_name"]
    host = request.META['HTTP_REFERER']
    response = requests.get(url=host+"api/search", params={'app_name': app_name})
    return render(request, 'productOverview.html', response.json())


def product(request):
	return render(request,'productOverview.html')


def review_form(request):
	return render(request,'writeReview.html')  	
	serializer = AppSerializer(app)
	return Response(data=serializer.data)

@api_view(['GET'])
def best_apps(request):
	res = {}	
	for genre_dict in App.objects.values('play_store_genre').distinct():
		genre = genre_dict['play_store_genre']
		apps = App.objects.filter(play_store_genre=genre).order_by('avg_rating')[:4]
		res[genre] = AppSerializer(apps, many=True).data
	return Response(data=res)

@api_view(['GET'])
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

@api_view(['GET'])
def counter(request):
	count_apps = App.objects.count()
	count_users = PlayStoreReview.objects.values('user_name').distinct()
	count_reviews = PlayStoreReview.objects.count()
	return Response({'apps': count_apps, 'users': count_users, 'reviews': count_reviews})
