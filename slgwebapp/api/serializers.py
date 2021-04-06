from rest_framework import serializers
from .models import *


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
        fields = '__all__'


class PlayStoreGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = '__all__'


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'


class QueryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryOption
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'