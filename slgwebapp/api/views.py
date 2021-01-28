from django.forms.models import model_to_dict
from django.http import JsonResponse
from .models import App
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def search(request):
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