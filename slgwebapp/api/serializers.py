from django.db.models import fields
from rest_framework import serializers
from .models import App, SiteReview

class AppSerializer(serializers.ModelSerializer):
	class Meta:
		model = App
		fields = '__all__'

class SiteReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = SiteReview
		fields = '__all__'