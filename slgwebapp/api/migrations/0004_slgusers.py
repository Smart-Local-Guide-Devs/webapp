# Generated by Django 3.1.4 on 2021-01-23 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210104_0223'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlgUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(default='Anonymous User', max_length=64)),
                ('user_img_link', models.URLField()),
                ('content', models.TextField()),
                ('up_vote_count', models.PositiveIntegerField()),
                ('app_id', models.ForeignKey(max_length=128, on_delete=django.db.models.deletion.CASCADE, to='api.app', unique=True)),
            ],
        ),
    ]
