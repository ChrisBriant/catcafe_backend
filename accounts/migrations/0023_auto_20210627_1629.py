# Generated by Django 3.1.3 on 2021-06-27 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_auto_20210627_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='hash',
            field=models.CharField(default='0x7ee5349f55c5661745733c65dd75772d', max_length=128),
        ),
    ]
