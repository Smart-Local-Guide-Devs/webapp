from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class App(models.Model):
	app_id = models.CharField(unique=True, max_length=128)
	app_name = models.CharField(max_length=64)
	playstore_link = models.URLField()
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
	icon_link = models.URLField()
	header_link = models.URLField()

	def __str__(self) -> str:
		return self.app_name

class SlgSiteReview(models.Model):
	user_name = models.CharField(default='Anonymous User' ,max_length=64)
	email_id = models.EmailField(max_length=256)
	content = models.TextField()

	def __str__(self) -> str:
		return self.review

class PlayStoreReview(models.Model):
	app = models.ForeignKey(to=App, on_delete=models.CASCADE)
	user_name = models.CharField(default='Anonymous User', max_length=64)
	user_img_link = models.URLField()
	content =  models.TextField()
	rating = models.SmallIntegerField(choices=[(i,i) for i in range(1,6)])
	up_vote_count = models.PositiveIntegerField()

	def __str__(self) -> str:
		return self.content

class QueryOption(models.Model):
	option = models.CharField(max_length=128, unique= True)

	def __str__(self) -> str:
		return self.option

class ReviewQuery(models.Model):
	query = models.CharField(max_length=256, unique=True)
	option_1 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='option_1')
	option_2 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='option_2')
	option_3 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='option_3')
	option_4 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='option_4')

	def __str__(self) -> str:
		return self.query

class Genre(models.Model):
	genre_name = models.CharField(max_length=32, unique=True)
	apps = models.ManyToManyField(to=App)
	query_1 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='query_1')
	query_2 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='query_2')
	query_3 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='query_3')
	query_4 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='query_4')

	def __str__(self) -> str:
		return self.genre_name

class Review(models.Model):
	app = models.ForeignKey(to=App, on_delete=models.CASCADE)
	user = models.ForeignKey(to=User, on_delete=models.CASCADE)
	content = models.TextField()
	rating = models.IntegerField(choices=[(i,i) for i in range(1,6)])
	general_query_1 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='general_query_1')
	general_choice_1 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='general_choice_1')
	general_query_2 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='general_query_2')
	general_choice_2 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='general_choice_2')
	genre_query_1 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='genre_query_1')
	genre_choice_1 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='genre_choice_1')
	genre_query_2 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='genre_query_2')
	genre_choice_2 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='genre_choice_2')
	genre_query_3 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='genre_query_3')
	genre_choice_3 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='genre_choice_3')
	genre_query_4 = models.ForeignKey(to=ReviewQuery, on_delete=models.PROTECT, related_name='genre_query_4')
	genre_choice_4 = models.ForeignKey(to=QueryOption, on_delete=models.PROTECT, related_name='genre_choice_4')

	def __str__(self) -> str:
		return self.content