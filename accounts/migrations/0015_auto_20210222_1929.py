# Generated by Django 3.1.3 on 2021-02-22 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20210222_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='hash',
            field=models.CharField(default='0xdbacb18f0bdb3717e27b9fd6d981e7d4', max_length=128),
        ),
    ]
