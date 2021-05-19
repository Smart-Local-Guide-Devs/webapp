from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(App)
admin.site.register(SlgSiteReview)
admin.site.register(Review)
admin.site.register(Genre)
admin.site.register(Query)
admin.site.register(QueryChoice)
admin.site.register(Visitors)