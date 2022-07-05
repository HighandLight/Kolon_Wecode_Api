from django.db import models

class TestCar(models.Model):
    number                  = models.CharField(max_length = 15)
    owner                   = models.CharField(max_length = 100)
    manufacturer            = models.CharField(max_length = 50)
    car_name                = models.CharField(max_length = 50)
    trim                    = models.CharField(max_length = 50)
    body_shape              = models.CharField(max_length = 50)
    color                   = models.CharField(max_length = 50)
    model_year              = models.CharField(max_length = 50)
    first_registration_year = models.CharField(max_length = 50)
    mileage                 = models.CharField(max_length = 50)
    engine                  = models.CharField(max_length = 50)
    transmission            = models.CharField(max_length = 50)
    factory_price           = models.BigIntegerField()
    transaction_price       = models.BigIntegerField()

    class Meta:
        db_table = 'test_cars'

class TestInsuranceHistory(models.Model):
    test_car = models.ForeignKey('TestCar', on_delete = models.CASCADE)
    history  = models.CharField(max_length = 50)

    class Meta:
        db_table = 'test_insurance_histories'

class TestTransactionHistory(models.Model):
    test_car = models.ForeignKey('TestCar', on_delete = models.CASCADE)
    history  = models.CharField(max_length = 50)

    class Meta:
        db_table = 'test_transaction_histories'