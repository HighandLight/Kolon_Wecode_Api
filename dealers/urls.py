from django.urls import path

from dealers.views import AdminSignUpView, AdminLoginView, AdminView, EstimateListView, EstimateDetailView, ConsultingView

urlpatterns = [
    path('/signup', AdminSignUpView.as_view()),
    path('/login', AdminLoginView.as_view()),
    path('', AdminView.as_view()),
    path('/estimates', EstimateListView.as_view()),
    path('/estimate/<int:estimate_id>', EstimateDetailView.as_view()),
    path('/consulting', ConsultingView.as_view()),
] 