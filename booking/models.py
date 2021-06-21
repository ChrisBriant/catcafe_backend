from django.db import models
from accounts.models import Account


class Slot(models.Model):
    date = models.DateTimeField(null=False)
    date_booked = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Account,on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date'], name='unique_slot')
        ]
