import json

from datetime import datetime, timedelta

import bcrypt
import jwt
from django.http import JsonResponse
from django.views import View
from django.conf import settings

from cars.models import Car

class SignInView(View):
    def post(self, request):
        # try:
        data = json.loads(request.body)
        car_number = data["car_number"]
        owner = data["owner"]
        car = Car.objects.get(car = car)

        if car is not None:
            return JsonResponse({'message': 'isnotnone'}, status=401)





# class SignUpView(View):
#     def post(self, request):
#         try :
#             data                    = json.loads(request.body)
#             car_number              = data['car_number']
#             owner                   = data['owner']
#             car_name                = data['car_name']
#             trim                    = data['trim']
#             body_shape              = data['body_shape']
#             color                   = data['color']
#             model_year              = data['model_year']
#             first_registration_year = data['first_registration_year']
#             engine                  = data['engine']
#             transmission            = data['transmission']
#             manufacturer            = data['manufacturer']
#             factory_price           = data['factory_price']
#             insurance_history       = data['insurance_history']
#             transaction_history     = data['transaction_history']
#             kakao_id                = data['kakao_id']
            
#             with transaction.atomic():
#                 car = Car.objects.create(
#                     car_number              = car_number,
#                     owner                   = owner,
#                     car_name                = car_name,
#                     trim                    = trim,
#                     body_shape              = body_shape,
#                     color                   = color,
#                     model_year              = model_year,
#                     first_registration_year = first_registration_year,
#                     engine                  = engine,
#                     transmission            = transmission,
#                     manufacturer            = manufacturer,
#                     factory_price           = factory_price,
#                     kakao_id                = kakao_id,
#                 )
#                 for insurance_history in insurance_history:
#                     InsuranceHistory.objects.create(
#                         car     = car,
#                         history = insurance_history,
#                     )
#                 for transaction_history in transaction_history:
#                     TransactionHistory.objects.create(
#                         car     = car,
#                         history = transaction_history,
#                     )
#                 access_token = jwt.encode({'id' : car.id}, SECRET_KEY, ALGORITHM)

#                 return JsonResponse({'Message': 'SUCCESS', 'Access_token': access_token}, status=200)