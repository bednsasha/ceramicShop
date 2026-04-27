from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.contrib import messages
from django.db import transaction
from products.models import Product, ProductSize
from .models import Cart, CartItem
from .forms import AddToCartForm


class CartMixin:
    def get_cart(self, request):
        if hasattr(request, 'cart'):
            return request.cart
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )
        request.session['cart_id'] = cart.id
        request.session.modified = True
        
        return cart


class CartModalView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size'
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal.html', context)


class AddToCartView(CartMixin, View):
    @transaction.atomic
    def post(self, request, slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)
        
        form = AddToCartForm(request.POST, product=product)
        
        if not form.is_valid():
            return JsonResponse({
                'error': 'Ошибка в данных формы',
                'errors': form.errors,
            }, status=400)
        
        
        size_id = form.cleaned_data.get('size_id')
        if size_id:
            product_size = get_object_or_404(
                ProductSize,
                id=size_id,
                product=product
            )
        else:
           
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                return JsonResponse({
                    'error': 'Нет доступных размеров'
                }, status=400)
        
        quantity = form.cleaned_data['quantity']
      
        if product_size.stock < quantity:
            return JsonResponse({
                'error': f'Доступно только {product_size.stock} шт.'
            }, status=400)
        
        
        existing_item = cart.items.filter(
            product=product,
            product_size=product_size,
        ).first()
        
        if existing_item:
            total_quantity = existing_item.quantity + quantity
            if total_quantity > product_size.stock:
                return JsonResponse({
                    'error': f'Нельзя добавить {quantity} шт. Доступно еще {product_size.stock - existing_item.quantity} шт.'
                }, status=400)
        
 
        cart_item = cart.add_product(product, product_size, quantity)
        
        request.session['cart_id'] = cart.id
        request.session.modified = True
        
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_modal.html', {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',
                    'product_size__size'
                ).order_by('-added_at')
            })
        else:
            return JsonResponse({
                'success': True,
                'total_items': cart.total_items,
                'subtotal': str(cart.subtotal),
                'message': f'{product.name} добавлен в корзину',
                'cart_item_id': cart_item.id
            })


class UpdateCartItemView(CartMixin, View):

    @transaction.atomic
    def post(self, request, item_id):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 0:
            return JsonResponse({'error': 'Неверное количество'}, status=400)
        
        if quantity == 0:
            cart_item.delete()
            message = 'Товар удален из корзины'
        else:
            if quantity > cart_item.product_size.stock:
                return JsonResponse({
                    'error': f'Доступно только {cart_item.product_size.stock} шт.'
                }, status=400)
            
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Количество обновлено'
     
        request.session['cart_id'] = cart.id
        request.session.modified = True
        
        if request.headers.get('HX-Request'):
            context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',
                    'product_size__size',
                ).order_by('-added_at')
            }
            return TemplateResponse(request, 'cart/cart_modal.html', context)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'total_items': cart.total_items,
            'subtotal': str(cart.subtotal),
            'item_total': str(cart_item.total_price) if quantity > 0 else 0
        })


class RemoveCartItemView(CartMixin, View):

    def post(self, request, item_id):
        cart = self.get_cart(request)
        
        try:
            cart_item = cart.items.get(id=item_id)
            product_name = cart_item.product.name
            cart_item.delete()
            
            request.session['cart_id'] = cart.id
            request.session.modified = True
            
            if request.headers.get('HX-Request'):
                context = {
                    'cart': cart,
                    'cart_items': cart.items.select_related(
                        'product',
                        'product_size__size',
                    ).order_by('-added_at')
                }
                return TemplateResponse(request, 'cart/cart_modal.html', context)
            
            return JsonResponse({
                'success': True,
                'message': f'{product_name} удален из корзины',
                'total_items': cart.total_items,
                'subtotal': str(cart.subtotal)
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Товар не найден'}, status=404)


class CartCountView(CartMixin, View):

    def get(self, request):
        cart = self.get_cart(request)
        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal),
            'subtotal_display': f"{cart.subtotal} ₽"
        })


class ClearCartView(CartMixin, View):
  
    def post(self, request):
        cart = self.get_cart(request)
        cart.clear()
        
        request.session['cart_id'] = cart.id
        request.session.modified = True
        
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_empty.html', {
                'cart': cart
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
            'total_items': 0,
            'subtotal': '0'
        })


class CartSummaryView(CartMixin, View):

    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size'
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_summary.html', context)


class CartCheckoutView(CartMixin, View):

    def get(self, request):
        cart = self.get_cart(request)
        
        if cart.total_items == 0:
            messages.warning(request, 'Корзина пуста. Добавьте товары для оформления заказа.')
            return redirect('products:catalog_all')
        
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size'
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_checkout.html', context)