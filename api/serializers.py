from rest_framework import serializers
from .models import *


class AppSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(
        "genre", many=True, source="genre_set", read_only=True
    )

    class Meta:
        model = App
        fields = [
            "app_id",
            "app_name",
            "app_summary",
            "min_installs",
            "icon_link",
            "genres",
            "avg_rating",
            "ratings_count",
            "reviews_count",
            "free",
        ]


class QueryChoiceSerializer(serializers.ModelSerializer):
    query = serializers.SlugRelatedField("query", queryset=Query.objects.all())

    class Meta:
        model = QueryChoice
        fields = ["query", "choice"]


class ReviewSerializer(serializers.ModelSerializer):
    app_id = serializers.SlugRelatedField(
        "app_id", source="app", queryset=App.objects.all()
    )
    app_name = serializers.SlugRelatedField(
        "app_name", source="app", queryset=App.objects.all()
    )
    app_icon_link = serializers.SlugRelatedField(
        "icon_link", source="app", queryset=App.objects.all()
    )
    username = serializers.SlugRelatedField(
        "username", source="user", queryset=User.objects.all()
    )
    query_choices = QueryChoiceSerializer(many=True)
    up_votes = serializers.IntegerField(source="up_voters.count", read_only=True)
    down_votes = serializers.IntegerField(source="down_voters.count", read_only=True)

    class Meta:
        model = Review
        fields = [
            "pk",
            "app_id",
            "app_name",
            "app_icon_link",
            "username",
            "content",
            "rating",
            "query_choices",
            "state",
            "city",
            "up_votes",
            "down_votes",
        ]

    def create(self, validated_data: dict):
        query_choices = validated_data.pop("query_choices")
        review = Review.objects.create(**validated_data)
        for query_choice in query_choices:
            query_choice, _ = QueryChoice.objects.get_or_create(**query_choice)
            review.query_choices.add(query_choice)
        return review


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = "__all__"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["genre"]
