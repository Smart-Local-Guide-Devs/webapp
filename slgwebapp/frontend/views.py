from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.contrib.auth.forms import UserCreationForm



# Create your views here.
def signup(request):
	form=UserCreationForm()
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
	context = {'form':form}
	return render(request, 'signup.html',context)
    #return render(request,'signup.html',context)


def index(request):
	return render(request,'home.html')

def product(request):
    return render(request,'productOverview.html')

def review_form(request):
    return render(request,'writeReview.html')    	

def login(request):
    return render(request,'login.html')   



def search(request):
    app_name = request.GET["app_name"]
    host = request.META['HTTP_REFERER']
    response = requests.get(url=host+"api/search", params={'app_name': app_name})
    return render(request, 'productOverview.html', response.json())