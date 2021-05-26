# Generated by Django 3.1.4 on 2021-05-23 18:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0010_merge_20210523_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='down_voters',
            field=models.ManyToManyField(blank=True, related_name='down_voters', to=settings.AUTH_USER_MODEL),
        ),
    ]
