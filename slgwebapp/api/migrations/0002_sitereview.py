# Generated by Django 3.1.4 on 2021-01-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=64)),
                ('email_id', models.EmailField(max_length=64)),
                ('review', models.TextField()),
            ],
        ),
    ]