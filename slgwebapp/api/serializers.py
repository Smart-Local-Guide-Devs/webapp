from rest_framework import serializers
from .models import App, SiteReview, AppReview

class AppSerializer(serializers.ModelSerializer):
	class Meta:
		model = App
		fields = '__all__'

class SiteReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = SiteReview
		fields = '__all__'

class AppReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppReview
		fields = '__all__'