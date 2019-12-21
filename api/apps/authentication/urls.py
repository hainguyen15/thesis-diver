from django.urls import path
from .views import LoginAPIView, RegistrationAPIView

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('auth/', LoginAPIView.as_view()),
    # TODO: refresh token
]