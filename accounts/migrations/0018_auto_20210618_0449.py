# Generated by Django 3.1.3 on 2021-06-18 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20210226_0509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='hash',
            field=models.CharField(default='0x6f4a59af851625da5a49eb1d6443b4a8', max_length=128),
        ),
    ]
