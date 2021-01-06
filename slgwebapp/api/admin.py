from django.contrib import admin
from .models import App, SiteReview, AppReview

# Register your models here.
admin.site.register(App)
admin.site.register(SiteReview)
admin.site.register(AppReview)