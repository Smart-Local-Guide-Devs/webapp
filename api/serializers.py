from django.db.models import fields
from rest_framework import serializers
from .models import *


class AppSerializer(serializers.ModelSerializer):
    genre_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = App
        fields = ["app_id", "app_name", "app_summary", "icon_link", "genre_set"]


class SlgSiteReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlgSiteReview
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = "__all__"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["genre"]
