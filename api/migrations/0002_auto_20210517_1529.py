# Generated by Django 3.1.4 on 2021-05-17 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='country',
            field=models.CharField(default='Not Available', max_length=128),
        ),
        migrations.AddField(
            model_name='review',
            name='state',
            field=models.CharField(default='Not Available', max_length=128),
        ),
    ]
