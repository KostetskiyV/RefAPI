from django.urls import path

from .views import *

app_name = 'authentication'
urlpatterns = [
    path('auth/', AuthAPIView.as_view()),
    path('profile/<str:phoneNumber>/', ProfileAPIView.as_view())
]