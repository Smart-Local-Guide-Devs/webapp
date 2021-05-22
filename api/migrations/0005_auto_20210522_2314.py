# Generated by Django 3.1.4 on 2021-05-22 17:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0004_auto_20210521_0121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='up_votes',
        ),
        migrations.AddField(
            model_name='review',
            name='up_voters',
            field=models.ManyToManyField(blank=True, related_name='up_voters', to=settings.AUTH_USER_MODEL),
        ),
    ]