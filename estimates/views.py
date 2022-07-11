import json
from datetime import datetime

from django.http  import JsonResponse
from django.db import transaction
from django.views import View

from cores.utils import login_decorator
from estimates.models import Estimate, EstimateCarImage
from notifications.models import SalesProcess, QuoteNotification, UserNotification

class EstimateView(View):
    @login_decorator
    # 견적서 작성
    def post(self, request): 
        try :
            data                     = json.loads(request.body)
            car                      = request.car
            # process_state : "주행거리"
            mileage                  = data['mileage']
            # process_state : "추가옵션"
            sunroof                  = data['sunroof']
            navigation               = data['navigation']
            ventilation_seat         = data['ventilation_seat']
            heated_seat              = data['heated_seat']
            electric_seat            = data['electric_seat']
            smart_key                = data['smart_key']
            leather_seat             = data['leather_seat']
            electric_folding_mirror  = data['electric_folding_mirror']
            # process_state : "추가입력"
            accident_status          = data['accident_status']
            spare_key                = data['spare_key']
            wheel_scratch            = data['wheel_scratch']
            outer_plate_scratch      = data['outer_plate_scratch']
            other_maintenance_repair = data['other_maintenance_repair']
            other_special            = data['other_special']
            # process_state : "사진등록"
            # process_state : "개인정보"
            address                  = data['address']
            phone_number             = data['phone_number']
            # process_state : "신청완료"
            process_state            = data['process_state']
            
            # 등록되어 있는 견적서가 이미 있을 경우 에러처리 [이전에 미리 확인 하나 서버 오류 등 발생 시 에러처리]
            if Estimate.objects.filter(car_id = car.id):
                return JsonResponse({'Message' : 'THE_ESTIMATE_ALREADY_EXISTS'}, status=404)
            # [transaction] 여러개의 create 처리 시 한건 이라도 처리 되지 않을 경우 전체 처리 X
            Estimate.objects.create(
                car_id                   = car.id,
                mileage                  = mileage,
                address                  = address,
                phone_number             = phone_number,
                sunroof                  = sunroof,
                navigation               = navigation,
                ventilation_seat         = ventilation_seat,
                heated_seat              = heated_seat,
                electric_seat            = electric_seat,
                smart_key                = smart_key,
                leather_seat             = leather_seat,
                electric_folding_mirror  = electric_folding_mirror,
                accident_status          = accident_status,
                spare_key                = spare_key,
                wheel_scratch            = wheel_scratch,
                outer_plate_scratch      = outer_plate_scratch,
                other_maintenance_repair = other_maintenance_repair,
                other_special            = other_special,
                process_state            = process_state,
            )
            
            return JsonResponse({'Message': 'SUCCESS'}, status=200)
        
        except KeyError: 
            return JsonResponse({'Message' : 'KEY_ERROR'}, status=400)
    # 견적서 보기
    @login_decorator
    def get(self, request): 
        try :
            estimate = Estimate.objects.get(car_id = request.car.id)
            
            results = {
                'mileage'                 : estimate.mileage,
                'address'                 : estimate.address,
                'phone_number'            : estimate.phone_number,
                'sunroof'                 : estimate.sunroof,
                'navigation'              : estimate.navigation,
                'ventilation_seat'        : estimate.ventilation_seat,
                'heated_seat'             : estimate.heated_seat,
                'electric_seat'           : estimate.electric_seat,
                'smart_key'               : estimate.smart_key,
                'leather_seat'            : estimate.leather_seat,
                'electric_folding_mirror' : estimate.electric_folding_mirror,
                'accident_status'         : estimate.accident_status,
                'spare_key'               : estimate.spare_key,
                'wheel_scratch'           : estimate.wheel_scratch,
                'outer_plate_scratch'     : estimate.outer_plate_scratch,
                'other_maintenance_repair': estimate.other_maintenance_repair,
                'other_special'           : estimate.other_special,
                'process_state'           : estimate.process_state,
            }
            
            return JsonResponse({'results': results}, status=200)
        # 등록되어 있는 견적서 없을 경우 에러처리
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)
    # 견적서 수정하기
    @login_decorator
    def patch(self, request): 
        try :
            data = json.loads(request.body)
            estimate = Estimate.objects.get(car_id = request.car.id)
            
            estimate.process_state            = data['process_state']
            estimate.mileage                  = data.get('mileage', estimate.mileage)
            estimate.address                  = data.get('address', estimate.address)
            estimate.phone_number             = data.get('phone_number', estimate.phone_number)
            estimate.sunroof                  = data.get('sunroof', estimate.sunroof)
            estimate.navigation               = data.get('navigation', estimate.navigation)
            estimate.ventilation_seat         = data.get('ventilation_seat', estimate.ventilation_seat)
            estimate.heated_seat              = data.get('heated_seat', estimate.heated_seat)
            estimate.electric_seat            = data.get('electric_seat', estimate.electric_seat)
            estimate.smart_key                = data.get('smart_key', estimate.smart_key)
            estimate.leather_seat             = data.get('leather_seat', estimate.leather_seat)
            estimate.electric_folding_mirror  = data.get('electric_folding_mirror', estimate.electric_folding_mirror)
            estimate.accident_status          = data.get('accident_status', estimate.accident_status)
            estimate.spare_key                = data.get('spare_key', estimate.spare_key)
            estimate.wheel_scratch            = data.get('wheel_scratch', estimate.wheel_scratch)
            estimate.outer_plate_scratch      = data.get('outer_plate_scratch', estimate.outer_plate_scratch)
            estimate.other_maintenance_repair = data.get('other_maintenance_repair', estimate.other_maintenance_repair)
            estimate.other_special            = data.get('other_special', estimate.other_special)
            estimate.save()
            # 견적서 작성 완료 될 경우 판매 프로세스 시작 
            if estimate.process_state == "신청완료":
                with transaction.atomic():
                    if SalesProcess.objects.filter(estimate_id = estimate.id).exists():
                        return JsonResponse({'Message' : 'THE_ESTIMATE_ALREADY_EXISTS'}, status=404)
                    else:
                        sales_process = SalesProcess.objects.create(
                            estimate        = estimate,
                            quote_requested = datetime.now(),
                            process_state   = '대기'
                        )
                        # 지도 API 구현 후 수정 필요
                return JsonResponse({'Message': 'REQUEST_ESTIMATE_SUCCESS'}, status=200)
            
            return JsonResponse({'Message': 'SUCCESS'}, status=200)
        # 기본 키에러
        except KeyError: 
            return JsonResponse({'Message' : 'KEY_ERROR'}, status=400)
        
        except transaction.TransactionManagementError:
            return JsonResponse({'Message': 'TransactionManagementError'}, status=400)
        # 등록되어 있는 견적서 없을 경우 에러처리
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)
    # 견적서 삭제하기
    @login_decorator
    def delete(self, request):
        try:
            estimate = Estimate.objects.get(car_id = request.car.id)
            EstimateCarImage.objects.filter(estimate_id = estimate.id).delete()
            estimate.delete()
            
            return JsonResponse({'Message': 'NO_CONTENT'}, status=200)
        # 등록되어 있는 견적서 없을 경우 에러처리
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)

class EstimateImageView(View):
    @login_decorator
    # 견적서 이미지 등록 및 수정(삭제 후 재등록)
    def post(self, request): 
        try :
            estimate = Estimate.objects.get(car_id = request.car.id)
            images        = request.FILES.getlist('image')
            image_infos   = request.POST.getlist('image_info')
            
            i = 0
            for i in range(len(images)):
                #이미 등록된 사진(사진정보)이 있을 경우 삭제
                if EstimateCarImage.objects.filter(image_info = image_infos[i]):
                    EstimateCarImage.objects.filter(estimate_id = estimate.id).delete()
                EstimateCarImage.objects.create(
                    estimate   = estimate,
                    image_info = image_infos[i],
                    image      = images[i],
                )
                i += 1
            # process_state 변경 
            estimate.process_state = "사진등록"
            estimate.save()
            return JsonResponse({'Message': 'SUCCESS'}, status=200)
        
        except KeyError: 
            return JsonResponse({'Message' : 'KEY_ERROR'}, status=400)
        
    # 견적서 이미지 확인
    @login_decorator
    def get(self, request): 
        estimate = Estimate.objects.get(car_id = request.car.id)
        
        results = {
            'image': [{
                'image_id'  : estimatecarimage.id,
                'image_info': estimatecarimage.image_info,
                'image'     : str(estimatecarimage.image),
            } for estimatecarimage in estimate.estimatecarimage_set.all()],
        }
        
        return JsonResponse({'results': results}, status=200)
    
    # 견적서 이미지 삭제
    @login_decorator
    def delete(self, request):
        try:
            estimate = Estimate.objects.get(car_id = request.car.id)
            EstimateCarImage.objects.filter(estimate_id = estimate.id).delete()
            
            return JsonResponse({'Message': 'NO_CONTENT'}, status=200)
        # 등록되어 있는 견적서 없을 경우 에러처리
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)

class EstimateDetailView(View):
    # 견적서 상세 내역 보기
    @login_decorator
    def get(self, request): 
        try :
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
                'insurance_history'      : [history.history for history in car.insurancehistory_set.all()],
                'transaction_history'    : [history.history for history in car.transactionhistory_set.all()],
                'estimate': [{
                    'mileage'                 : estimate.mileage,
                    'address'                 : estimate.address,
                    'phone_number'            : estimate.phone_number,
                    'sunroof'                 : estimate.sunroof,
                    'navigation'              : estimate.navigation,
                    'ventilation_seat'        : estimate.ventilation_seat,
                    'heated_seat'             : estimate.heated_seat,
                    'electric_seat'           : estimate.electric_seat,
                    'smart_key'               : estimate.smart_key,
                    'leather_seat'            : estimate.leather_seat,
                    'electric_folding_mirror' : estimate.electric_folding_mirror,
                    'accident_status'         : estimate.accident_status,
                    'spare_key'               : estimate.spare_key,
                    'wheel_scratch'           : estimate.wheel_scratch,
                    'outer_plate_scratch'     : estimate.outer_plate_scratch,
                    'other_maintenance_repair': estimate.other_maintenance_repair,
                    'other_special'           : estimate.other_special,
                    'process_state'           : estimate.process_state,
                    'image': [{
                        'image_info': estimatecarimage.image_info,
                        'image'     : str(estimatecarimage.image),
                    } for estimatecarimage in estimate.estimatecarimage_set.all()]
                } for estimate in car.estimate_set.all()]
            }
            
            return JsonResponse({'results': results}, status=200)
        # 등록되어 있는 견적서 없을 경우 에러처리
        except Estimate.DoesNotExist:
            return JsonResponse({'Message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)