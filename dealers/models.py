from django.db import models

from cores.models import TimeStampModel

class Dealer(TimeStampModel):
    branch          = models.ForeignKey('dealers.Branch', on_delete = models.CASCADE)
    level           = models.CharField(max_length = 200)
    dealer_id       = models.CharField(max_length = 100)
    dealer_password = models.CharField(max_length = 200)
    name            = models.CharField(max_length = 50)

    class Meta:
        db_table = 'dealers'

class Branch(TimeStampModel):
    name       = models.CharField(max_length = 100)
    address    = models.CharField(max_length = 200)
    latitude   = models.DecimalField(max_digits = 6, decimal_places = 6, default = 0)
    longitude = models.DecimalField(max_digits = 6, decimal_places = 6, default = 0)

    class Meta:
        db_table = 'branches'