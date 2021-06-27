# Generated by Django 3.1.3 on 2021-06-27 15:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0002_auto_20210621_0534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.IntegerField(validators=[django.core.validators.MaxValueValidator(8), django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='slot',
            name='unique_slot',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='customer',
        ),
        migrations.AddField(
            model_name='table',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='table',
            name='slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.slot'),
        ),
        migrations.AddConstraint(
            model_name='table',
            constraint=models.UniqueConstraint(fields=('slot', 'table_number'), name='unique_table_slot'),
        ),
    ]