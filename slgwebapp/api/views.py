from django.db.models import fields
from django.forms.models import model_to_dict
from django.http import JsonResponse
from .models import App

# Create your views here.
def search(request):
	app_name = request.GET['app_name']
	app = App.objects.get(app_name=app_name)
	return JsonResponse(model_to_dict(app))

def best5(request):
	genre = request.GET['genre']
	apps = App.objects.filter(genre=genre).order_by('avg_rating')
	res = {}
	for i, app in enumerate(apps.values()[:5]):
		res[i] = app
	return JsonResponse(res)

