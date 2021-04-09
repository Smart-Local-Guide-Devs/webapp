from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
import requests


def get_api_route(request):
    domain = get_current_site(request=request).domain
    return 'http://' + domain+'/api'

# Create your views here.


def index(request):
    top_users = requests.get(url=get_api_route(request)+'/top_users')
    counter = requests.get(url=get_api_route(request)+'/counter')
    best_apps = requests.get(url=get_api_route(request)+'/best_apps')
    return render(request, 'home.html', {'best_apps': best_apps.json(), 'counter': counter.json(), 'users': top_users.json()})


def search(request):
    search_query = request.GET['search_query']
    response = requests.get(url=get_api_route(
        request)+'/search', params={'search_query': search_query})
    return render(request, 'searchResult.html', {'search_results': response.json()})


def get_app(request):
    app_name = request.GET['app_name']
    response = requests.get(url=get_api_route(
        request)+'/get_app', params={'app_name': app_name}).json()
    ratings_count = response['app']['ratings_count']
    histogram = {'1_star_percent': response['app']['one_stars']*100/ratings_count,
                 '2_star_percent': response['app']['two_stars']*100/ratings_count,
                 '3_star_percent': response['app']['three_stars']*100/ratings_count,
                 '4_star_percent': response['app']['four_stars']*100/ratings_count,
                 '5_star_percent': response['app']['five_stars']*100/ratings_count, }
    return render(request, 'appPage.html', {'app': response['app'], 'histogram': histogram, 'reviews': response['reviews']})


def site_review(request):
    response = requests.post(url=get_api_route(
        request)+'/site_review', data=request.POST)
    return render(request, 'home.html', {'review_form': response.json()})


def app_review(request):
    if request.method == 'POST':
        response = requests.post(url=get_api_route(
            request)+'/app_review', data=request.POST)
        if(response.status_code == 400):
            print(response.text)
        response = requests.get(url=get_api_route(request)+'/app_review', params={'app_name': request.POST['app_name']})
    else:
        response = requests.get(url=get_api_route(request)+'/app_review', params={'app_name': request.GET['app_name']})
    return render(request, 'writeReview.html', response.json())


def login(request):
    return render(request, 'login.html')
