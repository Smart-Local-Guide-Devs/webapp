from django.forms.models import model_to_dict
from django.http import JsonResponse
from .models import App

# Create your views here.
def search(request):
	app_name = request.GET['app_name']
	app = App.objects.get(app_name=app_name)
	return JsonResponse(model_to_dict(app))
