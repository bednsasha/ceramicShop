# payment/views.py
import uuid
import logging
import json
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from yookassa import Configuration, Payment
from orders.models import Order
from cart.views import CartMixin

logger = logging.getLogger(__name__)

# Настройка YooKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_yookassa_payment(order, request):
    """
    Создание платежа в YooKassa
    """
    cart = CartMixin().get_cart(request)
    
    # Формируем список товаров для чека
    receipt_items = []
    for item in cart.items.select_related('product', 'product_size'):
        size_display = f"{item.product_size.size.get_attribute_type_display()}: {item.product_size.value}"
        description = f"{item.product.name} - {size_display}"
        
        receipt_items.append({
            "description": description[:128],  # YooKassa ограничение 128 символов
            "quantity": str(item.quantity),
            "amount": {
                "value": f"{float(item.product.price):.2f}",
                "currency": "RUB"
            },
            "vat_code": getattr(settings, 'YOOKASSA_VAT_CODE', 6),
            "payment_mode": "full_payment",
            "payment_subject": "commodity"
        })
    
    # Данные клиента для чека
    customer = {
        "email": order.email
    }
    if order.phone:
        customer["phone"] = order.phone
    
    try:
        idempotence_key = str(uuid.uuid4())
        
        payment_data = {
            "amount": {
                "value": f"{float(order.total_price):.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(
                    reverse('payment:yookassa_success')
                ) + f'?order_id={order.id}'
            },
            "capture": True,
            "description": f"Заказ #{order.id} в Ceramics Studio",
            "metadata": {
                "order_id": order.id,
                "user_id": order.user.id if order.user else None
            }
        }
        
        # Добавляем чек, если есть товары
        if receipt_items and customer:
            payment_data["receipt"] = {
                "customer": customer,
                "items": receipt_items
            }
        
        payment = Payment.create(payment_data, idempotence_key)
        
        # Сохраняем данные платежа
        order.yookassa_payment_id = payment.id
        order.yookassa_confirmation_url = payment.confirmation.confirmation_url
        order.payment_provider = 'yookassa'
        order.save()
        
        logger.info(f"Создан платеж YooKassa {payment.id} для заказа #{order.id}")
        return payment
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа YooKassa: {str(e)}")
        raise


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """
    Webhook для обработки статуса платежа от YooKassa
    """
    try:
        event = json.loads(request.body)
        logger.info(f"YooKassa webhook получен: {event.get('event')}")
        
        payment_id = event.get('object', {}).get('id')
        payment_status = event.get('object', {}).get('status')
        
        if payment_id and payment_status:
            try:
                order = Order.objects.get(yookassa_payment_id=payment_id)
                
                if payment_status == 'succeeded':
                    order.payment_status = 'succeeded'
                    order.status = 'processing'
                    order.save()
                    logger.info(f"Заказ #{order.id} успешно оплачен через YooKassa")
                    
                elif payment_status == 'canceled':
                    order.payment_status = 'canceled'
                    order.status = 'cancelled'
                    order.save()
                    logger.info(f"Платеж YooKassa для заказа #{order.id} отменен")
                    
            except Order.DoesNotExist:
                logger.warning(f"Заказ с payment_id {payment_id} не найден")
                
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Ошибка обработки webhook YooKassa: {str(e)}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)


def yookassa_success(request):
    """
    Страница успешной оплаты через YooKassa
    """
    order_id = request.GET.get('order_id')
    order = None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            
            # Очищаем корзину
            cart = CartMixin().get_cart(request)
            cart.clear()
            
        except Order.DoesNotExist:
            pass
    
    context = {'order': order}
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'payment/yookassa_success_content.html', context)
    return render(request, 'payment/yookassa_success.html', context)


def yookassa_cancel(request):
    """
    Страница отмены оплаты через YooKassa
    """
    order_id = request.GET.get('order_id')
    order = None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.payment_status = 'canceled'
            order.save()
        except Order.DoesNotExist:
            pass
    
    context = {
        'order': order,
        'message': 'Платеж был отменен. Вы можете повторить попытку в корзине.'
    }
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'payment/yookassa_cancel_content.html', context)
    return render(request, 'payment/yookassa_cancel.html', context)