from django.shortcuts import render
import requests

from api.models import ReviewFormInput

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
    app_name = request.GET["app_name"]
    host = request.META['HTTP_REFERER']
    response = requests.get(url=host+"api/search", params={'app_name': app_name})
    return render(request, 'productOverview.html', response.json())

def review_form_submission(request):
    print("Thanks for the review!!")
    product_name = request.POST["product_name"]

    review_form_input = ReviewFormInput(product_name=product_name)
    review_form_input.save()
    print("Thanks for the review!!")
    return render(request, 'writeReview.html')