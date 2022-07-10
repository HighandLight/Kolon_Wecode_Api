#cars/views.py

import json, jwt, requests

from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.db import transaction

from cars.models import Car, InsuranceHistory, TransactionHistory
from cars.utils import (
    login_decorator,
    validate_car_number,
)

class SignInView(View):
    def post(self, request):
        try:
            data       = json.loads(request.body)
            car_number = data["car_number"]
            owner      = data["owner"]
            car        = Car.objects.get(car_number = car_number)
            # name = Car.objects.get(owner = owner)
            print("======1======")
            if car is None:
                return JsonResponse({'message': 'INVALID_CAR_INFORMATION'}, status=401)
            # if name is None:
            #     return JsonResponse({'message' : 'INVALID_OWNER_NAME'}, status=401)
            print("======2======")
            exp_days     = 1
            payload      = {'id': car.id, 'exp': datetime.utcnow() + timedelta(days = exp_days)}
            access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            print("======3======")
            return JsonResponse({"message": "SUCCESS", "ACCESS_TOKEN": access_token}, status=200)
            print("======4======")
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        except Car.DoesNotExist:
            return JsonResponse({"message": "INVALID_CAR"}, status=401)
    
        except json.JSONDecodeError:
            return JsonResponse({"message": "JSON_DECODE_ERROR"}, status=400)

class SignUpView(View):
    def post(self, request):
        print("===========0===========")
        try :
            data                    = json.loads(request.body)
            car_number              = data['car_number']
            owner                   = data['owner']
            phone_number            = data['phone_number']
            car_name                = data['car_name']
            trim                    = data['trim']
            body_shape              = data['body_shape']
            color                   = data['color']
            model_year              = data['model_year']
            first_registration_year = data['first_registration_year']
            engine                  = data['engine']
            transmission            = data['transmission']
            manufacturer            = data['manufacturer']
            factory_price           = data['factory_price']
        # insurance_history       = data['insurance_history']
        # transaction_history     = data['transaction_history']
            kakao_id                = data['kakao_id']
            address                 = data['address']

            print("===========0.5===========")
            with transaction.atomic():
                car = Car.objects.create(
                    car_number              = car_number,
                    owner                   = owner,
                    phone_number            = phone_number,
                    car_name                = car_name,
                    trim                    = trim,
                    body_shape              = body_shape,
                    color                   = color,
                    model_year              = model_year,
                    first_registration_year = first_registration_year,
                    engine                  = engine,
                    transmission            = transmission,
                    manufacturer            = manufacturer,
                    factory_price           = factory_price,
                    kakao_id                = kakao_id,
                    address                 = address
                )
                print("===========1===========")

                for insurance_history in insurance_history:
                    InsuranceHistory.objects.create(
                        car     = car,
                        history = insurance_history,
                    )
                print("===========2===========")
                for transaction_history in transaction_history:
                    TransactionHistory.objects.create(
                        car     = car,
                        history = transaction_history,
                    )
                print("===========3===========")
                # access_token = jwt.encode({'id' : car.id}, SECRET_KEY, ALGORITHM)  

                exp_days     = 1
                payload      = {'id': car.id, 'exp': datetime.utcnow() + timedelta(days = exp_days)}
                access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

                return JsonResponse({'Message': 'SUCCESS', 'Access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({"message": "KEY_ERROR", "data" : data, "owner" : owner, "phone_number" : phone_number, "car_number" : car_number}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"message": "JSON_DECODE_ERROR"}, status=400)


class KakaoLoginView(View):
    def get(self, request):
        try:
            kakao_token_api = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type"  : "authorization_code",
                "client_id"   : settings.KAKAO_APPKEY,
                "redirect_uri": "http://127.0.0.1:8000/cars/kakao/callback",
                "code"        : request.GET.get("code")
            }

            access_token = requests.post(kakao_token_api, data=data, timeout = 1).json().get('access_token')
            user_info    = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f"Bearer {access_token}"}, timeout = 1).json()
            kakao_id          = user_info["id"]
            kakao_name        = user_info["properties"]["nickname"]
            kakao_email       = user_info["kakao_account"]["email"]
            

            user, is_created = Car.objects.get_or_create(
                defaults = {
                    "kakao_id"     : kakao_id,
                }
            )
            access_token = jwt.encode({"id" : user.id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
 
            if is_created:
                return JsonResponse({"message" : "ACCOUNT CREATED", "token" : access_token}, status=201)
                
            else:
                return JsonResponse({"message" : "SIGN IN SUCCESS", "token" : access_token}, status=200)
            
        except KeyError:
            return JsonResponse({'message' : "KEY_ERROR"}, status=400) 