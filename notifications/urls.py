from django.urls import path

from notifications.views import QuoteNotificationView, UserNotificationView

urlpatterns = [
    path('/admin', QuoteNotificationView.as_view()),
    path('', UserNotificationView.as_view()),
] 