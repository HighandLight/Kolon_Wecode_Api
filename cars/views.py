import json, jwt, requests

from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.db import transaction

from cars.models import Car, InsuranceHistory, TransactionHistory
from estimates.models import Estimate
from cars.utils import (
    login_decorator,
    validate_car_number,
)


class SignInView(View):
    # 로그인
    def post(self, request):
        try:
            data       = json.loads(request.body)
            car_number = data['car_number']
            owner      = data['owner']
            
            car = Car.objects.get(car_number = car_number, owner = owner)
            
            access_token = jwt.encode({'id' : car.id}, SECRET_KEY, ALGORITHM)
            
            if car.estimate_set.get(car_id = car.id).car.id == car.id:
                
                estimate = car.estimate_set.all()[0]
                
                if estimate.process_state == '신청완료':
                    # 견적서 신청 완료 일 경우
                    return JsonResponse({
                        'Message'      : 'SUCCESS_ESTIMATE_COMPLETION',
                        'estimate_id'  : estimate.id,
                        'process_state': estimate.process_state,
                        'ACCESS_TOKEN' : access_token
                    }, status=200)
                else:
                    # 견적서 중 일 경우
                    return JsonResponse({
                        'Message'      : 'SUCCESS_ESTIMATE_REGISTERING',
                        'estimate_id'  : estimate.id,
                        'process_state': estimate.process_state,
                        'ACCESS_TOKEN' : access_token
                    }, status=200)
                    
        #회원가입 만 진행 후 작성 한 견적서가 없을 경우 했을 경우
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'SUCCESS_ESTIMATE_REQUIRED', 'ACCESS_TOKEN' : access_token}, status = 200)
        except KeyError: 
            return JsonResponse({'Message': 'KEY_ERROR'}, status = 400)
        # 우리 데이터에 해당 차량번호 등록되어 있지 않을 경우 에러메세지
        except Car.DoesNotExist:
            return JsonResponse({'Message': 'MY_CAR_NOT_PRESENT_CAR_NUMBER'}, status = 400)
class SignUpView(View):
    #회원가입
    def post(self, request):
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
            insurance_history       = data['insurance_history']
            transaction_history     = data['transaction_history']
            kakao_id                = data['kakao_id']
            
            # 처음 등록한 차량번호와 다른 차량번호 입력 방지를 위한 에러처리
            if Car.objects.filter(car_number = car_number, owner = owner):
                return JsonResponse({'Message' : 'THE_CAR_NUMBER_AND_OWNER_ALREADY_EXISTS'}, status=404)
            
            # [transaction] 여러개의 create 처리 시 한건 이라도 처리 되지 않을 경우 전체 처리 X
            with transaction.atomic():
                car = Car.objects.create(
                    car_number              = car_number,
                    owner                   = owner,
                    car_name                = car_name,
                    phone_number            = phone_number,
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
                )
                for insurance_history in insurance_history:
                    InsuranceHistory.objects.create(
                        car     = car,
                        history = insurance_history,
                    )
                for transaction_history in transaction_history:
                    TransactionHistory.objects.create(
                        car     = car,
                        history = transaction_history,
                    )
                # 이후 처리를 위해 토큰 같이 발급
                access_token = jwt.encode({'id' : car.id}, SECRET_KEY, ALGORITHM)
                
                return JsonResponse({'Message': 'SUCCESS', 'ACCESS_TOKEN': access_token}, status=200)
        # [transaction] 에러처리
        except transaction.TransactionManagementError:
            return JsonResponse({'Message': 'TransactionManagementError'}, status=400)
        
        except KeyError: 
            return JsonResponse({'Message' : 'KEY_ERROR'}, status=400)

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