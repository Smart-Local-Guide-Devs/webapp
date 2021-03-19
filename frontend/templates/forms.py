from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
	phone = forms.CharField(max_length=15)
	class Meta:
		model = User
		fields = ['username','email','phone','password1','password2']