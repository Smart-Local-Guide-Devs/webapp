from django.contrib import admin
from .models import App, SlgSiteReview, Review, PlayStoreReview, Genre, ReviewQuery, QueryOption

# Register your models here.
admin.site.register(App)
admin.site.register(SlgSiteReview)
admin.site.register(Review)
admin.site.register(PlayStoreReview)
admin.site.register(Genre)
admin.site.register(ReviewQuery)
admin.site.register(QueryOption)
