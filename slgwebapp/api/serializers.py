from rest_framework import serializers
from .models import App, SlgSiteReview, PlayStoreReview, Genre, ReviewQuery, QueryOption

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


class PlayStoreGenreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Genre
		fields= '__all__'

class ReviewQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = ReviewQuery
		fields= '__all__'

class QueryOptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = QueryOption
		fields= '__all__'