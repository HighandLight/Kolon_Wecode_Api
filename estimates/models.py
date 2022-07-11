from django.db import models

from cores.models import TimeStampModel

class Estimate(TimeStampModel):
    car                      = models.ForeignKey('cars.Car', on_delete = models.CASCADE)
    mileage                  = models.CharField(max_length = 100, null = True)
    address                  = models.CharField(max_length = 100, null = True)
    phone_number             = models.CharField(max_length = 30, null = True)
    sunroof                  = models.BooleanField(default = False)
    navigation               = models.BooleanField(default = False)
    ventilation_seat         = models.BooleanField(default = False)
    heated_seat              = models.BooleanField(default = False)
    electric_seat            = models.BooleanField(default = False)
    leather_seat             = models.BooleanField(default = False)
    smart_key                = models.BooleanField(default = False)
    electric_folding_mirror  = models.BooleanField(default = False)
    accident_status          = models.TextField(null = True)
    spare_key                = models.IntegerField(default = 0)
    wheel_scratch            = models.IntegerField(default = 0)
    outer_plate_scratch      = models.IntegerField(default = 0)
    other_maintenance_repair = models.TextField(null = True)
    other_special            = models.TextField(null = True)
    process_state            = models.CharField(max_length = 100, null = True)

    class Meta:
        db_table = 'estimates'

class EstimateCarImage(TimeStampModel):
    estimate   = models.ForeignKey('estimates.Estimate', on_delete = models.CASCADE)
    image_info = models.CharField(max_length = 200)
    image      = models.ImageField(upload_to='images/',blank=True, null=True)

    class Meta:
        db_table = 'estimate_car_images'