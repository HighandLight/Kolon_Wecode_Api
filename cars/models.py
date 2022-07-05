from django.db import models

from cores.models import TimeStampModel

class Car(TimeStampModel):
    user                    = models.ForeignKey('users.User', on_delete = models.CASCADE)
    car_name                = models.CharField(max_length = 50)
    trim                    = models.CharField(max_length = 50)
    body_shape              = models.CharField(max_length = 50)
    color                   = models.CharField(max_length = 50)
    model_year              = models.CharField(max_length = 50)
    first_registration_year = models.CharField(max_length = 50)
    engine                  = models.CharField(max_length = 50)
    transmission            = models.CharField(max_length = 50)
    manufacturer            = models.CharField(max_length = 50)
    factory_price           = models.BigIntegerField()

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

        
class Estimate(TimeStampModel):
    car                      = models.ForeignKey('cars.Car', on_delete = models.CASCADE)
    mileage                  = models.CharField(max_length = 100)
    address                  = models.CharField(max_length = 100)
    phone_number             = models.CharField(max_length = 30)
    sunroof                  = models.BooleanField()
    navigation               = models.BooleanField()
    ventilation_seat         = models.BooleanField()
    heated_seat              = models.BooleanField()
    electric_seat            = models.BooleanField()
    smart_key                = models.BooleanField()
    leather_seat             = models.BooleanField()
    electric_folding_mirror  = models.BooleanField()
    accident_status          = models.BooleanField()
    spare_key                = models.IntegerField()
    wheel_scratch            = models.IntegerField()
    outer_plate_scratch      = models.IntegerField()
    other_maintenance_repair = models.TextField()
    other_special            = models.TextField()

    class Meta:
        db_table = 'estimates'

class EstimateCarImage(models.Model):
    estimate   = models.ForeignKey('cars.Estimate', on_delete = models.CASCADE)
    image_info = models.CharField(max_length = 200)
    image      = models.CharField(max_length = 200)

    class Meta:
        db_table = 'estimate_car_images'