from rest_framework import serializers
from .models import App, SlgSiteReview, PlayStoreReview

class AppSerializer(serializers.ModelSerializer):
	class Meta:
		model = App
		fields = '__all__'

class SlgSiteReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = SlgSiteReview
		fields = '__all__'

class PlayStoreReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlayStoreReview
		fields= '__all__'
