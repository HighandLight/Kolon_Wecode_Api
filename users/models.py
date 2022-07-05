from django.db import models

from cores.models import TimeStampModel

class User(TimeStampModel):
    owner      = models.CharField(max_length = 15)
    car_number = models.CharField(max_length = 15, unique = True)
    kakao_id   = models.BigIntegerField(null=True)
    
    class Meta:
        db_table = 'users'