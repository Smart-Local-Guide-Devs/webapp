# Generated by Django 3.1.4 on 2021-05-20 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_visitors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Visitors',
        ),
        migrations.AlterField(
            model_name='review',
            name='country',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='review',
            name='state',
            field=models.CharField(max_length=128),
        ),
    ]
