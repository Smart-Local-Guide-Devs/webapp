from django.db import models

# Create your models here.
class App(models.Model):
	app_id = models.CharField(unique=True, blank=False, max_length=128)
	app_name = models.CharField(blank=False, max_length=64)
	playstore_link = models.URLField(blank=False)
	installs_count = models.PositiveIntegerField()
	avg_rating = models.FloatField()
	ratings_count = models.IntegerField()
	reviews_count = models.IntegerField()
	is_free = models.BooleanField()
	app_size = models.CharField(max_length=8)
	genre = models.CharField(max_length=32)
	icon_link = models.URLField(blank=False)
	header_link = models.URLField(blank=False)
	release_date = models.DateField()

class SiteReview(models.Model):
	user_name = models.CharField(blank=False, max_length=64)
	email_id = models.EmailField(max_length=64)
	review = models.TextField()