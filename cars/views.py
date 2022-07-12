import json, jwt, requests

from datetime import datetime, timedelta

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Sum
from django.db        import transaction

from kolon_wecode.settings  import SECRET_KEY, ALGORITHM, KAKAO_APPKEY, KAKAO_REDIRECT_URI
from cars.models            import Car, InsuranceHistory, TransactionHistory
from estimates.models       import Estimate
from testcar.models         import TestCar
from cores.utils            import login_decorator

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
                        'message'      : 'SUCCESS_ESTIMATE_COMPLETION',
                        'estimate_id'  : estimate.id,
                        'process_state': estimate.process_state,
                        'access_token' : access_token
                    }, status=200)
                else:
                    # 견적서 중 일 경우
                    return JsonResponse({
                        'message'      : 'SUCCESS_ESTIMATE_REGISTERING',
                        'estimate_id'  : estimate.id,
                        'process_state': estimate.process_state,
                        'access_token' : access_token
                    }, status=200)
                    
        #회원가입 만 진행 후 작성 한 견적서가 없을 경우 했을 경우
        except Estimate.DoesNotExist:
            return JsonResponse({'message': 'SUCCESS_ESTIMATE_REQUIRED', 'access_token' : access_token}, status = 200)
        except KeyError: 
            return JsonResponse({'message': 'KEY_ERROR'}, status = 400)
        # 우리 데이터에 해당 차량번호 등록되어 있지 않을 경우 에러메세지
        except Car.DoesNotExist:
            return JsonResponse({'message': 'MY_CAR_NOT_PRESENT_CAR_NUMBER'}, status = 400)
        
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
                return JsonResponse({'message' : 'THE_CAR_NUMBER_AND_OWNER_ALREADY_EXISTS'}, status=404)
            
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
                
                return JsonResponse({'message': 'SUCCESS', 'access_token': access_token}, status=200)
        # [transaction] 에러처리
        except transaction.TransactionManagementError:
            return JsonResponse({'message': 'TransactionManagementError'}, status=400)
        
        except KeyError: 
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)

class KakaoLoginView(View):
    def get(self, request):
        try:
            kakao_token_api = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type"  : "authorization_code",
                "client_id"   : KAKAO_APPKEY,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code"        : request.GET.get("code")
            }
            
            access_token = requests.post(kakao_token_api, data=data, timeout = 1).json().get('access_token')
            user_info    = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f"Bearer {access_token}"}, timeout = 1).json()
            kakao_id     = user_info["id"]
            
            return JsonResponse({"message" : "SUCCESS", "kakao_id" : kakao_id}, status=200)
            
        except KeyError:
            return JsonResponse({'message' : "KEY_ERROR"}, status=400) 

class CarNumberCheckView(View):
    # DB에 차량번호 조회만 진행 
    def post(self, request):
        try:
            data       = json.loads(request.body)
            car_number = data['car_number']
            
            Car.objects.get(car_number = car_number)
            
            return JsonResponse({'message': 'THE_CAR_NUMBER_ALREADY'}, status=200)
            
        except KeyError: 
            return JsonResponse({'message': 'KEY_ERROR'}, status = 400)
        # 우리 데이터에 해당 차량번호 있지 않을 경우 에러메세지 -> 회원가입 유도 필요
        except Car.DoesNotExist:
            return JsonResponse({'message': 'MY_CAR_NOT_PRESENT_CAR_NUMBER'}, status = 400)

class Car365APIView(View):
    # 추후 국토부 API사용시 불러올 정보를 가정한 내용
    def get(self, request): 
        try :
            car_number = request.GET['car_number']
            owner      = request.GET['owner']
            
            # 처음 등록한 차량번호와 다른 차량번호 (이미 DB에 등록되어 있는 정보) 입력 방지를 위한 에러처리
            if Car.objects.filter(car_number = car_number, owner = owner):
                return JsonResponse({'message' : 'THE_CAR_NUMBER_AND_OWNER_ALREADY_EXISTS'}, status=404)
            
            #차량번호와 소유자명이 다를 경우 에러처리
            if not TestCar.objects.filter(number = car_number, owner = owner).exists():
                return JsonResponse({'message' : 'INVALID_CAR_NUMBER_OR_OWNER'}, status=404)
            
            # 추후 국토부 API를 가정한 DB
            testcar = TestCar.objects.get(number = car_number, owner = owner)
            
            results = {
                'car_number'             : testcar.number,
                'owner'                  : testcar.owner,
                'manufacturer'           : testcar.manufacturer,
                'car_name'               : testcar.car_name,
                'trim'                   : testcar.trim,
                'body_shape'             : testcar.body_shape,
                'color'                  : testcar.color,
                'model_year'             : testcar.model_year,
                'first_registration_year': testcar.first_registration_year,
                'mileage'                : testcar.mileage,
                'engine'                 : testcar.engine,
                'transmission'           : testcar.transmission,
                'factory_price'          : testcar.factory_price,
                'transaction_price'      : testcar.transaction_price,
                'insurance_history'      : [history.history for history in testcar.testinsurancehistory_set.all()],
                'transaction_history'    : [history.history for history in testcar.testtransactionhistory_set.all()]
            }
            
            return JsonResponse({'message': 'SUCCESS', 'results': results}, status=200)
        
        except KeyError: 
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)

class CarInformationView(View):
    # 회원가입 이후 등록된 내 차량 정보 확인              
    @login_decorator
    def get(self, request): 
        car = request.car
        
        results = {
            'car_number'             : car.car_number,
            'owner'                  : car.owner,
            'manufacturer'           : car.manufacturer,
            'car_name'               : car.car_name,
            'trim'                   : car.trim,
            'body_shape'             : car.body_shape,
            'color'                  : car.color,
            'model_year'             : car.model_year,
            'first_registration_year': car.first_registration_year,
            'engine'                 : car.engine,
            'transmission'           : car.transmission,
            'factory_price'          : car.factory_price,
            'insurance_history'      : [history.history for history in car.insurancehistory_set.all()],
            'transaction_history'    : [history.history for history in car.transactionhistory_set.all()]
        }
        
        return JsonResponse({'results': results}, status=200)
        
    # 차량 관련 전체 정보 삭제하기
    @login_decorator
    def delete(self, request):
        car = request.car
        car.estimate_set.all()[0].estimatecarimage_set.all().delete()
        car.estimate_set.all().delete()
        car.insurancehistory_set.all().delete()
        car.transactionhistory_set.all().delete()
        car.delete()
        
        return JsonResponse({'message': 'NO_CONTENT'}, status=200)

class CarPriceView(View):
    @login_decorator
    # 차량 시세 보기
    def get(self, request): 
        # 차량시세 그래프 용 차량이름, 트림
        cars_1 = TestCar.objects.filter(car_name = request.car.car_name, trim = request.car.trim)
        
        transaction = [{
            'model_year': car.model_year,
            'price'     : car.transaction_price,
        }for car in cars_1]
        
        # 차량시세 그래프 용 차량이름, 트림, 연식
        cars_2 = TestCar.objects.filter\
            (car_name = request.car.car_name, trim = request.car.trim, model_year = request.car.model_year)
        price = cars_2.aggregate(Sum('transaction_price'))
        # 차량 예상가격
        estimated_price = price['transaction_price__sum'] / len(cars_2)
        
        # 차량시세 그래프 용 차량이름, 트림 개수 / 추후 x개 이하 일 경우 데이터가 부족하다는 문구 띄울 예정
        count = len(cars_2)
        
        return JsonResponse({'estimated_price': int(estimated_price), 'transaction_count' : count, 'transaction': transaction}, status=200)