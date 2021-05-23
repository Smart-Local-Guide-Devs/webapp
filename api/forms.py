from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class CreateUserForm(UserCreationForm):
	phone = forms.CharField(max_length=15)
	name = forms.CharField(max_length=50)
	class Meta:
		model = User
		fields = ['username','name','email','phone','password1','password2']

class SlgUserForm(UserCreationForm):
	class Meta:
		model = SlgUser
		fields = '__all__'
		exclude = ['user']