# Generated by Django 3.1.3 on 2021-06-27 16:44

import booking.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20210627_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.IntegerField(validators=[booking.models.validate_table]),
        ),
    ]