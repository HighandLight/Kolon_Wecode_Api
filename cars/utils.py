import re
from datetime import datetime

import jwt
from django.http            import JsonResponse
from django.conf            import settings
from django.core.exceptions import ValidationError

from cars.models import Car

def validate_car_number(car_number):
    REGEX_CAR = "^d{3,4}\[가-힣]{1}\d{4}$"
    
    if not re.match(REGEX_CAR, car_number):
        raise ValidationError("INVALID_CAR_NUMBER")


def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload      = jwt.decode(access_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            request.user = Car.objects.get(id=payload['id'])

            print(access_token)

            return func(self, request, *args, **kwargs)

        except Car.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status=400)
            
        except jwt.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status=400)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "EXPIRED_TOKEN"},print(access_token), status = 400)

    return wrapper