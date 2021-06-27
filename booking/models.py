from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Account
from django.core.validators import MaxValueValidator, MinValueValidator

class Slot(models.Model):
    date = models.DateTimeField(null=False)
    date_booked = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


    # class Meta:
    constraints = [
        models.UniqueConstraint(fields=['date'], name='unique_slot')
    ]

def validate_table(value):
    if value not in range(1,9):
        print('validating',value, type(value))
        raise ValidationError(
            ('Table number does not exist'),
            params={'table_number': value},
        )


class Table(models.Model):
    customer = models.ForeignKey(Account,on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot,on_delete=models.CASCADE)
    table_number = models.IntegerField( validators=[validate_table])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['slot','table_number'], name='unique_table_slot')
        ]
