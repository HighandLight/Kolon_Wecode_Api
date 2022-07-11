import json, jwt
from json.decoder import JSONDecodeError

from django.db.models import Sum
from django.http  import JsonResponse
from django.db import transaction
from django.views import View

from kolon_wecode.settings  import SECRET_KEY, ALGORITHM
from cores.utils import login_decorator, admin_login_decorator
from cars.models import Car, InsuranceHistory, TransactionHistory
from testcar.models import TestCar
from estimates.models import Estimate, EstimateCarImage
from notifications.models import SalesProcess, QuoteNotification, UserNotification

class QuoteNotificationView(View):
    # admin 알람 기능 / 딜러 지정 되지 않은 내역만 필터링
    @admin_login_decorator
    def get(self, request):
        notifications = QuoteNotification.objects.filter(branch_id=request.dealer.branch_id, dealer_assign = False)
        
        results = [{
            'branch'       : notification.branch.name,
            'car_number'   : notification.sales_process.estimate.car.car_number,
            'dealer_assign': notification.dealer_assign,
        }for notification in notifications]
        
        
        return JsonResponse({'results': results}, status=200)

class UserNotificationView(View):
    # 고객 알람 기능 
    @login_decorator
    def get(self, request):
        car        = request.car
        notifications = car.estimate_set.all()[0].salesprocess_set.all()[0].usernotification_set.all()
        
        results = [{
            'notification_id': notification.id,
            'car_number'     : notification.sales_process.estimate.car.car_number,
            'car_number'     : notification.sales_process.estimate.car.car_number,
            'content'        : notification.content,
            'read'           : notification.read,
            'create_at'      : notification.created_at,
        }for notification in notifications]
        
        return JsonResponse({'results': results}, status=200)
    
    @login_decorator
    def patch(self, request):
        car           = request.car
        notifications = car.estimate_set.all()[0].salesprocess_set.all()[0].usernotification_set.all()
        
        results = [{
            'car_number': notification.sales_process.estimate.car.car_number,
            'content'   : notification.content,
            'create_at' : notification.created_at,
        }for notification in notifications]
        
        return JsonResponse({'results': results}, status=200)

