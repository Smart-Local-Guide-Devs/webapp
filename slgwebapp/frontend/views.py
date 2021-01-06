from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
import requests

# Create your views here.
def index(request):
    domain=get_current_site(request=request).domain
    response = requests.get(url='http://'+domain+'/api/best_apps')
    return render(request=request, template_name='home.html', context={'best_apps': response.json()})

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

def site_review(request):
    domain = get_current_site(request=request).domain
    response = requests.post(url='http://'+domain+'/api/site_review', data=request.POST)
    return render(request=request, template_name='home.html', context={'review_form': response.json()})

