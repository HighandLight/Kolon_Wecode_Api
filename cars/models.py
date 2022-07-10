from ctypes import addressof
from django.db import models

from cores.models import TimeStampModel

class Car(TimeStampModel):
    address                 = models.CharField(max_length = 100, null = True)
    phone_number            = models.CharField(max_length = 100, null = True)
    owner                   = models.CharField(max_length = 15)
    car_number              = models.CharField(max_length = 15, unique = True)
    kakao_id                = models.BigIntegerField(null=True)
    car_name                = models.CharField(max_length = 50, null = True)
    trim                    = models.CharField(max_length = 50, null = True)
    body_shape              = models.CharField(max_length = 50, null = True)
    color                   = models.CharField(max_length = 50, null = True)
    model_year              = models.CharField(max_length = 50, null = True)
    first_registration_year = models.CharField(max_length = 50, null = True)
    engine                  = models.CharField(max_length = 50, null = True)
    transmission            = models.CharField(max_length = 50, null = True)
    manufacturer            = models.CharField(max_length = 50, null = True)
    factory_price           = models.BigIntegerField(null = True)

    class Meta:
        db_table = 'cars'

class InsuranceHistory(models.Model):
    car     = models.ForeignKey('cars.Car', on_delete = models.CASCADE)
    history = models.CharField(max_length = 50)

    class Meta:
        db_table = 'insurance_histories'

class TransactionHistory(models.Model):
    car     = models.ForeignKey('cars.Car', on_delete = models.CASCADE)
    history = models.CharField(max_length = 50)

    class Meta:
        db_table = 'transaction_histories'