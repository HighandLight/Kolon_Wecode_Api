import jwt
import json

from django.http  import JsonResponse

from kolon_wecode.settings import SECRET_KEY, ALGORITHM
from cars.models import Car
from dealers.models import Dealer

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload      = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            request.car = Car.objects.get(id= payload['id'])

        except jwt.exceptions.DecodeError:
            return JsonResponse({'Message' : 'INVALID_TOKEN'}, status = 400)

        except Car.DoesNotExist:
            return JsonResponse({'Message' : 'INVALID_USER'}, status = 400)

        return func(self, request, *args, **kwargs)
    return wrapper

def admin_login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token   = request.headers.get('Authorization', None)
            payload        = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            request.dealer = Dealer.objects.get(id= payload['id'])

        except jwt.exceptions.DecodeError:
            return JsonResponse({'Message' : 'INVALID_TOKEN'}, status = 400)

        except Dealer.DoesNotExist:
            return JsonResponse({'Message' : 'INVALID_USER'}, status = 400)

        return func(self, request, *args, **kwargs)
    return wrapper
