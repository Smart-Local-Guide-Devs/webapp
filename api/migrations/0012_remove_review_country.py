# Generated by Django 3.1.4 on 2021-05-24 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_review_down_voters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='country',
        ),
    ]