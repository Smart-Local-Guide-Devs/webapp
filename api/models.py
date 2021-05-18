from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class App(models.Model):
    app_id = models.CharField(unique=True, max_length=128)
    app_name = models.CharField(max_length=128)
    app_summary = models.CharField(max_length=256)
    min_installs = models.PositiveIntegerField()
    avg_rating = models.FloatField()
    ratings_count = models.PositiveIntegerField()
    reviews_count = models.PositiveIntegerField()
    free = models.BooleanField()
    icon_link = models.URLField()
    similar_apps = models.ManyToManyField(to="self", blank=True)

    def __str__(self) -> str:
        return self.app_name


class SlgSiteReview(models.Model):
    username = models.CharField(max_length=128, blank=True)
    email_id = models.EmailField(max_length=256)
    content = models.TextField()

    def __str__(self) -> str:
        return self.content


class Query(models.Model):
    query = models.CharField(max_length=256, unique=True)

    def __str__(self) -> str:
        return self.query


class Genre(models.Model):
    genre = models.CharField(max_length=128, unique=True)
    apps = models.ManyToManyField(to=App, blank=True)
    queries = models.ManyToManyField(to=Query, blank=True)

    def __str__(self) -> str:
        return self.genre


class QueryChoice(models.Model):
    query = models.ForeignKey(to=Query, on_delete=models.CASCADE)
    choice = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self) -> str:
        return self.query.query + ": " + str(self.choice)


class Review(models.Model):
    app = models.ForeignKey(to=App, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    query_choices = models.ManyToManyField(to=QueryChoice, blank=True)
    country = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    up_votes = models.PositiveIntegerField(blank=True, default=1)

    def __str__(self) -> str:
        return self.content
