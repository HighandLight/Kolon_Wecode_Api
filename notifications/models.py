from django.db import models

from cores.models import TimeStampModel

class SalesProcess(models.Model):
    estimate          = models.ForeignKey('estimates.Estimate', on_delete = models.CASCADE)
    quote_requested   = models.DateTimeField()
    dealer_assigned   = models.DateTimeField()
    dealer_consulting = models.DateTimeField()
    selling_requested = models.DateTimeField()
    selling_completed = models.DateTimeField()
    termination       = models.DateTimeField()

    class Meta: 
        db_table = 'sales_process'

class QuoteNotification(TimeStampModel):
    sales_process = models.ForeignKey('notifications.SalesProcess', on_delete = models.CASCADE)
    branch        = models.ForeignKey('dealers.Branch', on_delete = models.CASCADE)
    dealer_assign = models.BooleanField()

    class Meta:
        db_table = 'quote_notifications'

class UserNotification(TimeStampModel):
    sales_process = models.ForeignKey('notifications.SalesProcess', on_delete = models.CASCADE)
    name          = models.CharField(max_length = 50)
    read          = models.BooleanField()

    class Meta:
        db_table = 'user_notifications'