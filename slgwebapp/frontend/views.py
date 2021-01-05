from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
import requests

# Create your views here.
def index(request):
	return render(request,'home.html')

def product(request):
    return render(request,'productOverview.html')

def review_form(request):
    return render(request,'writeReview.html')    	

def login(request):
    return render(request,'login.html')   

def search(request):
    app_name = request.GET['app_name']
    domain = get_current_site(request=request).domain
    response = requests.get(url='http://'+domain+'/api/search', params={'app_name': app_name})
    return render(request, 'productOverview.html', response.json()[0])

