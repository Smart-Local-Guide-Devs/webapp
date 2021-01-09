# Generated by Django 3.1.4 on 2021-01-03 20:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0002_sitereview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='ratings_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='app',
            name='reviews_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='sitereview',
            name='email_id',
            field=models.EmailField(max_length=256),
        ),
        migrations.AlterField(
            model_name='sitereview',
            name='user_name',
            field=models.CharField(default='Anonymous User', max_length=64),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField()),
                ('stars', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('props', models.TextField(blank=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.app')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
