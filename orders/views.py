from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import View
from .forms import OrderForm
from .models import Order, OrderItem
from cart.views import CartMixin
from cart.models import Cart
from products.models import ProductSize
from django.shortcuts import get_object_or_404
from payment.views import create_yookassa_payment
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class CheckoutView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        logger.debug(f"Checkout view: session_key={request.session.session_key}, cart_id={cart.id}, total_items={cart.total_items}, subtotal={cart.subtotal}")

        if cart.total_items == 0:
            logger.warning("Cart is empty, redirecting to cart page")
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/empty_cart.html', {'message': 'Your cart is empty'})
            return redirect('cart:cart_modal')

        total_price = cart.subtotal
        logger.debug(f"Total price: {total_price}")

        form = OrderForm(user=request.user)
        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.select_related('product', 'product_size__size').order_by('-added_at'),
            'total_price': total_price,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = self.get_cart(request)
        
        if cart.total_items == 0:
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/empty_cart.html', {'message': 'Корзина пуста'})
            return redirect('cart:cart_modal')
        
        payment_provider = request.POST.get('payment_provider')
        
        form = OrderForm(request.POST, user=request.user)
        
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                company=form.cleaned_data['company'],
                address1=form.cleaned_data['address1'],
                address2=form.cleaned_data['address2'],
                city=form.cleaned_data['city'],
                country=form.cleaned_data['country'],
                province=form.cleaned_data['province'],
                postal_code=form.cleaned_data['postal_code'],
                phone=form.cleaned_data['phone'],
                special_instructions='',
                total_price=cart.subtotal,
                payment_provider=payment_provider,
            )
            
            # Создаем элементы заказа
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.product_size,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            try:
                payment_url = None
                
                if payment_provider == 'yookassa':
                    payment = create_yookassa_payment(order, request)
                    payment_url = payment.confirmation.confirmation_url
                
                # Очищаем корзину
                cart.clear()
                
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=200)
                    response['HX-Redirect'] = payment_url
                    return response
                
                return redirect(payment_url)
                
            except Exception as e:
                logger.error(f"Ошибка создания платежа: {e}")
                order.delete()
                
                context = {
                    'form': form,
                    'cart': cart,
                    'cart_items': cart.items.all(),
                    'total_price': cart.subtotal,
                    'error_message': 'Ошибка при создании платежа. Попробуйте позже.'
                }
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'orders/checkout_content.html', context)
                return render(request, 'orders/checkout.html', context)
        
        # Если форма не валидна
        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.all(),
            'total_price': cart.subtotal,
        }
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)