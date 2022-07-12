import re
import jwt
import json

from django.http            import JsonResponse
from django.core.exceptions import ValidationError

from kolon_wecode.settings import SECRET_KEY, ALGORITHM
from cars.models           import Car
from dealers.models        import Dealer


def validate_car_number(car_number):
    REGEX_CAR = "^d{3,4}\[가-힣]{1}\d{4}$"
    
    if not re.match(REGEX_CAR, car_number):
        raise ValidationError("INVALID_CAR_NUMBER")

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload      = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            request.car = Car.objects.get(id= payload['id'])

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status = 400)

        except Car.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status = 400)

        return func(self, request, *args, **kwargs)
    return wrapper

def admin_login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token   = request.headers.get('Authorization', None)
            payload        = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            request.dealer = Dealer.objects.get(id= payload['id'])

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status = 400)

        except Dealer.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status = 400)

        return func(self, request, *args, **kwargs)
    return wrapper
