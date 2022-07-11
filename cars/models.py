from django.db import models

from cores.models import TimeStampModel

class Car(TimeStampModel):
    owner                   = models.CharField(max_length = 15)
    car_number              = models.CharField(max_length = 15, unique = True)
    phone_number            = models.CharField(max_length = 20)
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

    
class Completion(TimeStampModel):
    user_phone_number        = models.CharField(max_length = 20)
    owner                    = models.CharField(max_length = 15)
    car_number               = models.CharField(max_length = 15, unique = True)
    car_name                 = models.CharField(max_length = 50, null = True)
    trim                     = models.CharField(max_length = 50, null = True)
    body_shape               = models.CharField(max_length = 50, null = True)
    color                    = models.CharField(max_length = 50, null = True)
    model_year               = models.CharField(max_length = 50, null = True)
    first_registration_year  = models.CharField(max_length = 50, null = True)
    engine                   = models.CharField(max_length = 50, null = True)
    transmission             = models.CharField(max_length = 50, null = True)
    manufacturer             = models.CharField(max_length = 50, null = True)
    factory_price            = models.BigIntegerField(null = True)
    kakao_id                 = models.BigIntegerField(null = True)
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
    quote_requested          = models.DateTimeField(null = True)
    dealer_assigned          = models.DateTimeField(null = True)
    dealer_consulting        = models.DateTimeField(null = True)
    selling_requested        = models.DateTimeField(null = True)
    selling_completed        = models.DateTimeField(null = True)
    termination              = models.DateTimeField(null = True)
    process_state            = models.CharField(max_length=100, null = True)
    dealer_name              = models.CharField(max_length = 20)
    branch_name              = models.CharField(max_length = 20)
    content                  = models.TextField()
