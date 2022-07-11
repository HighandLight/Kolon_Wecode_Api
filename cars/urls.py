from django.urls import path

from .views import SignInView, SignUpView, KakaoLoginView, CarNumberCheckView, Car365APIView, CarInformationView, CarPriceView
urlpatterns = [
    path ('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/kakao/callback', KakaoLoginView.as_view()),
    path('/number', CarNumberCheckView.as_view()),
    path('/car365API', Car365APIView.as_view()),
    path('/info', CarInformationView.as_view()),
    path('/price', CarPriceView.as_view()),
] 