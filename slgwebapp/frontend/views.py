from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout


# Create your views here.
def signup(request):
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
	
    


def index(request):
	return render(request,'home.html')

def product(request):
    return render(request,'productOverview.html')

def review_form(request):
    return render(request,'writeReview.html')    	

def signin(request):
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
	



def search(request):
    app_name = request.GET["app_name"]
    host = request.META['HTTP_REFERER']
    response = requests.get(url=host+"api/search", params={'app_name': app_name})
    return render(request, 'productOverview.html', response.json())