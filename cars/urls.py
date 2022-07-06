from django.urls import path

from .views import SignInView#, SignUpView

urlpatterns = [
    # path ('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
]