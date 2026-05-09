from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),
    path('yookassa/success/', views.yookassa_success, name='yookassa_success'),
    path('yookassa/cancel/', views.yookassa_cancel, name='yookassa_cancel')
]