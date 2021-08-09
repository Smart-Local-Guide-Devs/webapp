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
    state = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    up_voters = models.ManyToManyField(to=User, blank=True, related_name="up_voters")
    down_voters = models.ManyToManyField(
        to=User, blank=True, related_name="down_voters"
    )

    def __str__(self) -> str:
        return self.content


class Visitor(models.Model):
    ip = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.visitor


class SlgUser(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	phone = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	profile_pic_url = models.TextField(null=True)

	def __str__(self):
		return self.name



