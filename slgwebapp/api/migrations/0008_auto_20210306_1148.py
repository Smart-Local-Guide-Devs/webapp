# Generated by Django 3.1.6 on 2021-03-06 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_query'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='query_1',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='query',
            name='query_2',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='query',
            name='query_3',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='query',
            name='query_4',
            field=models.CharField(max_length=128),
        ),
    ]
