from django.urls import path

from .views import SignInView, SignUpView, KakaoLoginView

urlpatterns = [
    path ('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/kakao/callback', KakaoLoginView.as_view()),
]