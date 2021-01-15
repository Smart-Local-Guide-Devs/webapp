from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class App(models.Model):
	app_id = models.CharField(unique=True, null=False, max_length=128)
	app_name = models.CharField(null=False, max_length=64)
	playstore_link = models.URLField(null=False)
	installs_count = models.PositiveIntegerField()
	avg_rating = models.FloatField()
	ratings_count = models.PositiveIntegerField()
	reviews_count = models.PositiveIntegerField()
	is_free = models.BooleanField()
	app_size = models.CharField(max_length=8)
	genre = models.CharField(max_length=32)
	icon_link = models.URLField()
	header_link = models.URLField()
	release_date = models.DateField()

	def __str__(self) -> str:
		return self.app_name

class SiteReview(models.Model):
	user_name = models.CharField(default='Anonymous User' ,max_length=64)
	email_id = models.EmailField(blank=False ,max_length=256)
	review = models.TextField(blank=False)

	def __str__(self) -> str:
		return self.review

class AppReview(models.Model):
	app = models.ForeignKey(to=App, on_delete=models.CASCADE, null=False)
	#user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False)
	review = models.TextField()
	stars = models.IntegerField(choices=[(i,i) for i in range(1,6)])
	genre = models.CharField(max_length=100, default='base')


# anonymous user review model
