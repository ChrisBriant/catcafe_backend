# Generated by Django 3.1.3 on 2021-06-18 04:50

import cats.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('age', models.IntegerField()),
                ('food', models.CharField(max_length=50)),
                ('toy', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=10)),
                ('breed', models.CharField(max_length=50)),
                ('picture', models.FileField(upload_to=cats.models.image_path_handler)),
            ],
        ),
    ]
