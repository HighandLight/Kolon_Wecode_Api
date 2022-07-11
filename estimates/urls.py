from django.urls import path

from estimates.views import EstimateView, EstimateImageView, EstimateDetailView

urlpatterns = [
    path('', EstimateView.as_view()),
    path('/image', EstimateImageView.as_view()),
    path('/detail', EstimateDetailView.as_view()),
] 