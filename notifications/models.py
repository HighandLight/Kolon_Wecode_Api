from django.db import models

from cores.models import TimeStampModel

class SalesProcess(models.Model):
    estimate          = models.ForeignKey('estimates.Estimate', on_delete = models.CASCADE)
    quote_requested   = models.DateTimeField(null = True)
    dealer_assigned   = models.DateTimeField(null = True)
    dealer_consulting = models.DateTimeField(null = True)
    selling_requested = models.DateTimeField(null = True)
    selling_completed = models.DateTimeField(null = True)
    termination       = models.DateTimeField(null = True)
    process_state     = models.CharField(max_length=100, null = True)

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
    content       = models.CharField(max_length = 100)
    read          = models.BooleanField()

    class Meta:
        db_table = 'user_notifications'