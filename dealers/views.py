import json
import re
import bcrypt
import jwt
from datetime import datetime
from datetime import timedelta

from django.http            import JsonResponse
from django.views           import View
from django.db              import transaction
from django.db.models       import Q
from kolon_wecode.settings  import SECRET_KEY, ALGORITHM

from notifications.models import QuoteNotification, UserNotification, SalesProcess
from cores.utils          import admin_login_decorator
from dealers.models       import Dealer, Consulting, Branch
from estimates.models     import Estimate

class AdminSignUpView(View):
    #딜러 회원가입
    def post(self, request): 
        try: 
            data            = json.loads(request.body)
            dealer_id       = data['id']
            PASSWORD_REGEX  = r"^(?=.{8,16}$)(?=.*[a-z])(?=.*[0-9]).*$"
            dealer_password = data['password']
            
            if Dealer.objects.filter(dealer_id = dealer_id):
                return JsonResponse({'message' : 'THE_DEALER_ID_ALREADY_EXISTS'}, status=400)
            
            if not re.match(PASSWORD_REGEX, dealer_password):
                return JsonResponse({'message' : 'INVALID_PASSWORD'}, status=400)
            
            hashed_password = bcrypt.hashpw(dealer_password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
            
            Dealer.objects.create(
                dealer_id       = dealer_id,
                dealer_password = hashed_password,
                name            = data['name'],
                level           = data['level'],
                branch_id       = data['branch_id'],
            ) 
            return JsonResponse({'message' : 'SUCCESS'}, status=201)
            
        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status=400)

class AdminLoginView(View):
    #딜러 로그인
    def post(self, request):
        try:
            data = json.loads(request.body) 
            
            dealer_id       = data['id']
            dealer_password = data['password']
            
            dealer = Dealer.objects.get(dealer_id = dealer_id)
            
            if not bcrypt.checkpw(dealer_password.encode('utf-8'), dealer.dealer_password.encode('utf-8')):
                return JsonResponse({'message': 'INVALID_PASSWORD'}, status = 401)
            
            access_token = jwt.encode({'id' : dealer.id}, SECRET_KEY, ALGORITHM)
            
            return JsonResponse({
                'message'     : 'SUCCESS',
                'access_token': access_token,
                'name'        : dealer.name,
                'level'       : dealer.level,
                'branch'      : dealer.branch.name
            }, status=200)
            
        except KeyError: 
            return JsonResponse({'message': 'KeyError'}, status = 400)
        
        except Dealer.DoesNotExist:
            return JsonResponse({'message': 'INVALID_ID'}, status = 404)

class AdminView(View):
    @admin_login_decorator
    #딜러 기본 정보 확인
    def get(self, request):
        dealer = request.dealer
        
        results = {
            'dealer_id': dealer.id,
            'name'     : dealer.name,
            'level'    : dealer.level,
            'branch'   : dealer.branch.name
        }
        
        return JsonResponse({'results':results}, status=200)

# admin 견적서 리스트 페이지
class EstimateListView(View):
    @admin_login_decorator
    def get(self, request):
        #페이지네이션
        offset        = int(request.GET.get('offset', 0))
        limit         = int(request.GET.get('limit', 12))
        start_date    = request.GET.get('start_date')
        end_date      = request.GET.get('end_date')
        process_state = request.GET.getlist('state')
        branch_name   = request.GET.get('branch_name')
        dealer_name   = request.GET.get('dealer_name')
        
        dealer = request.dealer
        # Sales Consultant일 경우 해당 지점의 견적서만 확인 가능
        if dealer.level == "Sales Consultant":
            q = Q()
            if process_state:
                q &= Q(sales_process__process_state__in=process_state)
                
            if dealer_name:
                q &= Q(sales_process__estimate__consulting__dealer__name=dealer_name)
                
            if start_date != None or end_date != None:
                start_date   = datetime.strptime(start_date, '%Y-%m-%d')
                end_date     = datetime.strptime(end_date, '%Y-%m-%d')
                data_delta   = timedelta(days=1)
                new_end_date = end_date + data_delta
                q &= Q(sales_process__estimate__created_at__range=[start_date, new_end_date])
            
            q |= Q(branch_id=dealer.branch_id)
            
            quote_notifications = QuoteNotification.objects.filter(q).distinct().order_by('-id')[offset:offset+limit]
            # 해당 지점의 Sales Consultant 이름
            info = {
                'branch' : dealer.branch.name,
                'dealers': [{
                    'dealer_id'  : dealer.id,
                    'dealer_name': dealer.name,
                }for dealer in dealer.branch.dealer_set.all()]
            }
            
            results = [{
                'estimate_id'          : quote_notification.sales_process.estimate.id,
                'owner'                : quote_notification.sales_process.estimate.car.owner,
                'phone_number'         : quote_notification.sales_process.estimate.phone_number,
                'car_number'           : quote_notification.sales_process.estimate.car.car_number,
                'manufacturer'         : quote_notification.sales_process.estimate.car.manufacturer,
                'car_name'             : quote_notification.sales_process.estimate.car.car_name,
                'trim'                 : quote_notification.sales_process.estimate.car.trim,
                'model_year'           : quote_notification.sales_process.estimate.car.model_year,
                'estimate_request_date': quote_notification.sales_process.estimate.created_at,
                'dealer'               : [consulting.dealer.name for consulting in \
                    quote_notification.sales_process.estimate.consulting_set.all()],
                'branch'               : quote_notification.branch.name,
                'sales_process_id'     : quote_notification.sales_process.id,
                'quote_requested'      : quote_notification.sales_process.quote_requested,
                'dealer_assigned'      : quote_notification.sales_process.dealer_assigned,
                'dealer_consulting'    : quote_notification.sales_process.dealer_consulting,
                'selling_requested'    : quote_notification.sales_process.selling_requested,
                'selling_completed'    : quote_notification.sales_process.selling_completed,
                'termination'          : quote_notification.sales_process.termination,
            }for quote_notification in quote_notifications]
            
            return JsonResponse({'info': info, 'results': results}, status=200)
        # Showroom Manager일 경우 전체 지점의 견적 확인 가능
        if dealer.level == "Showroom Manager":
            q = Q()
            if process_state:
                q &= Q(sales_process__process_state__in=process_state)
                
            if branch_name:
                q &= Q(branch__name=branch_name)
                
            if dealer_name:
                q &= Q(sales_process__estimate__consulting__dealer__name=dealer_name)
                
            if start_date != None or end_date != None:
                start_date   = datetime.strptime(start_date, '%Y-%m-%d')
                end_date     = datetime.strptime(end_date, '%Y-%m-%d')
                data_delta   = timedelta(days=1)
                new_end_date = end_date + data_delta
                q &= Q(sales_process__estimate__created_at__range=[start_date, new_end_date])
            quote_notifications = QuoteNotification.objects.filter(q).distinct()[offset:offset+limit]
            branches            = Branch.objects.all()
            # 전체 지점 이름과 지점의 속해 있는데 전체 직원 이름
            info = [{
                'branch' : branch.name,
                'dealers': [{
                    'dealer_id'  : dealer.id,
                    'dealer_name': dealer.name,
                }for dealer in branch.dealer_set.all()]
            }for branch in branches]
            
            results = [{
                'estimate_id'          : quote_notification.sales_process.estimate.id,
                'owner'                : quote_notification.sales_process.estimate.car.owner,
                'phone_number'         : quote_notification.sales_process.estimate.phone_number,
                'car_number'           : quote_notification.sales_process.estimate.car.car_number,
                'manufacturer'         : quote_notification.sales_process.estimate.car.manufacturer,
                'car_name'             : quote_notification.sales_process.estimate.car.car_name,
                'trim'                 : quote_notification.sales_process.estimate.car.trim,
                'model_year'           : quote_notification.sales_process.estimate.car.model_year,
                'estimate_request_date': quote_notification.sales_process.estimate.created_at,
                'dealer'               : [consulting.dealer.name for consulting in \
                    quote_notification.sales_process.estimate.consulting_set.all()],
                'branch'               : quote_notification.branch.name,
                'sales_process_id'     : quote_notification.sales_process.id,
                'quote_requested'      : quote_notification.sales_process.quote_requested,
                'dealer_assigned'      : quote_notification.sales_process.dealer_assigned,
                'dealer_consulting'    : quote_notification.sales_process.dealer_consulting,
                'selling_requested'    : quote_notification.sales_process.selling_requested,
                'selling_completed'    : quote_notification.sales_process.selling_completed,
                'termination'          : quote_notification.sales_process.termination,
            }for quote_notification in quote_notifications]
            
            return JsonResponse({'info': info, 'results': results}, status=200)

class EstimateDetailView(View):
    @admin_login_decorator
    def get(self, request, estimate_id):
        try:
            dealer = request.dealer
            # Sales Consultant일 경우 해당 지점의 견적서인지 다시 체크
            if dealer.level == "Sales Consultant":
                estimate = Estimate.objects.get(id=estimate_id)
                branch_check = estimate.salesprocess_set.all()[0].quotenotification_set.filter(branch_id=dealer.branch_id)[0]
                if branch_check: 
                    results = {
                        'estimate_id'             : estimate.id,
                        'owner'                   : estimate.car.owner,
                        'phone_number'            : estimate.phone_number,
                        'address'                 : estimate.address,
                        'estimate_request_date'   : estimate.created_at,
                        'manufacturer'            : estimate.car.manufacturer,
                        'car_name'                : estimate.car.car_name,
                        'trim'                    : estimate.car.trim,
                        'body_shape'              : estimate.car.body_shape,
                        'color'                   : estimate.car.color,
                        'model_year'              : estimate.car.model_year,
                        'first_registration_year' : estimate.car.first_registration_year,
                        'engine'                  : estimate.car.engine,
                        'transmission'            : estimate.car.transmission,
                        'insurance_history'       : 
                            [history.history for history in estimate.car.insurancehistory_set.all()],
                        'transaction_history'     : 
                            [history.history for history in estimate.car.transactionhistory_set.all()],
                        'mileage'                 : estimate.mileage,
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
                        'estimate_image'          : [{
                            'image_id'  : estimatecarimage.id,
                            'image_info': estimatecarimage.image_info,
                            'image'     : str(estimatecarimage.image),
                        } for estimatecarimage in estimate.estimatecarimage_set.all()],
                        'sales_process'           : [{
                            'sales_process_id' : sales_process.id,
                            'quote_requested'  : sales_process.quote_requested,
                            'dealer_assigned'  : sales_process.dealer_assigned,
                            'dealer_consulting': sales_process.dealer_consulting,
                            'selling_requested': sales_process.selling_requested,
                            'selling_completed': sales_process.selling_completed,
                            'termination'      : sales_process.termination,
                        }for sales_process in estimate.salesprocess_set.all()],
                        'consulting':[{
                            'breanch': consulting.dealer.branch.name,
                            'dealer' : consulting.dealer.name,
                            'content': consulting.content
                        } for consulting in estimate.consulting_set.all()]
                    }
                    return JsonResponse({'results':results}, status=200)
            # Showroom Manager일 경우 지점 상관없이 확인 가능
            if dealer.level == "Showroom Manager":
                estimate = Estimate.objects.get(id=estimate_id)
                results = {
                    'estimate_id'             : estimate.id,
                    'owner'                   : estimate.car.owner,
                    'phone_number'            : estimate.phone_number,
                    'address'                 : estimate.address,
                    'estimate_request_date'   : estimate.created_at,
                    'manufacturer'            : estimate.car.manufacturer,
                    'car_name'                : estimate.car.car_name,
                    'trim'                    : estimate.car.trim,
                    'body_shape'              : estimate.car.body_shape,
                    'color'                   : estimate.car.color,
                    'model_year'              : estimate.car.model_year,
                    'first_registration_year' : estimate.car.first_registration_year,
                    'engine'                  : estimate.car.engine,
                    'transmission'            : estimate.car.transmission,
                    'insurance_history'       : 
                        [history.history for history in estimate.car.insurancehistory_set.all()],
                    'transaction_history'     : 
                        [history.history for history in estimate.car.transactionhistory_set.all()],
                    'mileage'                 : estimate.mileage,
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
                    'estimate_image'          : [{
                        'image_id'  : estimatecarimage.id,
                        'image_info': estimatecarimage.image_info,
                        'image'     : str(estimatecarimage.image),
                    } for estimatecarimage in estimate.estimatecarimage_set.all()],
                    'sales_process'           : [{
                        'sales_process_id' : sales_process.id,
                        'quote_requested'  : sales_process.quote_requested,
                        'dealer_assigned'  : sales_process.dealer_assigned,
                        'dealer_consulting': sales_process.dealer_consulting,
                        'selling_requested': sales_process.selling_requested,
                        'selling_completed': sales_process.selling_completed,
                        'termination'      : sales_process.termination,
                    }for sales_process in estimate.salesprocess_set.all()],
                    'consulting':[{
                        'breanch': consulting.dealer.branch.name,
                        'dealer' : consulting.dealer.name,
                        'content': consulting.content
                    } for consulting in estimate.consulting_set.all()]
                }
                return JsonResponse({'results':results}, status=200)
                
        except Estimate.DoesNotExist:
            return JsonResponse({'message': 'ESTIMATE_DOES_NOT_EXIST'}, status = 404)
        
        except IndexError:
            return JsonResponse({'message': 'INVALID_BRANCH'}, status = 404)

class ConsultingView(View):
    @admin_login_decorator
    # 딜러 지정
    def post(self, request):
        try :
            data        = json.loads(request.body)
            estimate_id = data['estimate_id']
            dealer_id   = data['dealer_id']
            # 이미 진행 되고 있는 컨설팅이 있을 경우 에러 처리 / 수정으로 추가 진행 필요
            if Consulting.objects.filter(estimate_id = estimate_id):
                return JsonResponse({'message' : 'THE_CONSULTING_ALREADY_EXISTS'}, status=404)
            # [transaction] 여러개의 create 처리 시 한건 이라도 처리 되지 않을 경우 전체 처리 X
            with transaction.atomic():
                consulting = Consulting.objects.create(
                    estimate_id = estimate_id,
                    dealer_id   = dealer_id,
                )
                #판매 프로세스 '딜러 배정 '시간 작성
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                
                sales_process.process_state   = '딜러배정'
                sales_process.dealer_assigned = datetime.now()
                sales_process.save()
                #딜러 알림 끄기
                quote_notification               = sales_process.quotenotification_set.all()[0]
                quote_notification.dealer_assign = True
                quote_notification.branch_id     = consulting.dealer.branch.id
                quote_notification.save()
                # 고객 알림 작성
                UserNotification.objects.create(
                    sales_process = sales_process,
                    content       = '차량 판매를 위해 담당SC가 배정되었습니다.',
                    read          = False
                )
                
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        
        except transaction.TransactionManagementError:
            return JsonResponse({'message': 'TransactionManagementError'}, status=400)
        
        except KeyError: 
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        
    # 상담 내용 작성 및 판매 프로세스 변경
    @admin_login_decorator
    def patch(self, request): 
        try :
            data        = json.loads(request.body)
            dealer      = request.dealer
            estimate_id = data['estimate_id']
            process_state      = data['status']
            
            if process_state == "딜러배정":
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                if not sales_process.dealer_consulting and sales_process.selling_requested and sales_process.selling_completed == "null".exists():
                    return JsonResponse({'message' : 'INVALID_SALES_PROCESS'}, status=404)
                pass
            
            if process_state == "방문상담":
                #판매 프로세스 '방문상담 '시간 작성
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                
                sales_process.process_state = process_state
                sales_process.dealer_consulting = datetime.now()
                sales_process.save()
                # 고객 알림 작성
                UserNotification.objects.create(
                    sales_process = sales_process,
                    content       = '차량 판매를 위해 SC 상담이 진행중입니다.',
                    read          = False
                )
                
            if process_state == "판매요청":
                #판매 프로세스 '방문상담 '시간 작성
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                
                sales_process.process_state = process_state
                sales_process.selling_requested = datetime.now()
                sales_process.save()
                # 고객 알림 작성
                UserNotification.objects.create(
                    sales_process = sales_process,
                    content       = '차량의 판매 요청이 진행중입니다.',
                    read          = False
                )
                
            if process_state == "판매완료":
                #판매 프로세스 '방문상담 '시간 작성
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                
                sales_process.process_state = process_state
                sales_process.selling_completed = datetime.now()
                sales_process.save()
                # 고객 알림 작성
                UserNotification.objects.create(
                    sales_process = sales_process,
                    content       = '차량이 판매 완료 되었습니다.',
                    read          = False
                )
                
            if process_state == "상담종료":
                #판매 프로세스 '상담종료 '시간 작성
                sales_process = SalesProcess.objects.get(estimate_id = estimate_id)
                
                sales_process.process_state = process_state
                sales_process.termination   = datetime.now()
                sales_process.save()
                # 상담 중단 될 경우 
                UserNotification.objects.create(
                    sales_process = sales_process,
                    content       = '상담이 종료 되었습니다.',
                    read          = False
                )
            
            consulting = Consulting.objects.get(estimate_id = estimate_id, dealer_id = dealer.id)
            
            consulting.content = data.get('content', consulting.content)
            consulting.save()
            
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        # 기본 키에러
        except KeyError: 
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        
        except transaction.TransactionManagementError:
            return JsonResponse({'message': 'TransactionManagementError'}, status=400)
        # 등록되어 있는 컨설팅이 없거나, 지정 된 딜러가 아닐 경우 에러처리
        except Consulting.DoesNotExist:
            return JsonResponse({'message': 'CONSULTING_DOES_NOT_EXIST'}, status = 404)