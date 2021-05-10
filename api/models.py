from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class App(models.Model):
    app_id = models.CharField(unique=True, max_length=128)
    app_name = models.CharField(max_length=64)
    app_description = models.TextField()
    app_summary = models.TextField()
    play_store_genre = models.CharField(max_length=32)
    min_installs = models.PositiveIntegerField()
    avg_rating = models.FloatField()
    ratings_count = models.PositiveIntegerField()
    reviews_count = models.PositiveIntegerField()
    one_stars = models.PositiveIntegerField()
    two_stars = models.PositiveIntegerField()
    three_stars = models.PositiveIntegerField()
    four_stars = models.PositiveIntegerField()
    five_stars = models.PositiveIntegerField()
    free = models.BooleanField()

    def __str__(self) -> str:
        return self.app_name


class SlgSiteReview(models.Model):
    user_name = models.CharField(default="Anonymous User", max_length=64)
    email_id = models.EmailField(max_length=256)
    content = models.TextField()

    def __str__(self) -> str:
        return self.review


class Option(models.Model):
    option = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.option


class Query(models.Model):
    query = models.CharField(max_length=256, unique=True)
    options = models.ManyToManyField(to=Option)

    def __str__(self) -> str:
        return self.query


class Genre(models.Model):
    genre_name = models.CharField(max_length=32, unique=True)
    apps = models.ManyToManyField(to=App)
    queries = models.ManyToManyField(to=Query)

    def __str__(self) -> str:
        return self.genre_name


class QueryOption(models.Model):
    query = models.ForeignKey(to=Query, on_delete=models.CASCADE)
    option = models.ForeignKey(to=Option, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.query.query + " : " + self.option.option


class Review(models.Model):
    app = models.ForeignKey(to=App, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    query_options = models.ManyToManyField(to=QueryOption)
    up_votes = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return self.content
