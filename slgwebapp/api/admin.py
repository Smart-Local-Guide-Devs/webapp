from django.contrib import admin
from .models import App, SiteReview, Review,SlgUser

# Register your models here.
admin.site.register(App)
admin.site.register(SiteReview)
admin.site.register(Review)
admin.site.register(SlgUser)