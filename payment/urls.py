from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),
    path('success/', views.yookassa_success, name='success'),
    path('cancel/', views.yookassa_cancel, name='cancel'),
]