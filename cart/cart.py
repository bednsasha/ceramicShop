from decimal import Decimal
from django.shortcuts import get_object_or_404
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, product_size, quantity=1, override_quantity=False):
        product_id = str(product.id)
        size_id = str(product_size.id)

        # Создаем уникальный ключ: product_id + size_id
        cart_key = f"{product_id}_{size_id}"

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'product_id': product.id,
                'size_id': product_size.id,
                'size_type': product_size.size.attribute_type,
                'size_value': str(product_size.value),
                'quantity': 0,
                'price': str(product.price),
                'product_name': product.name,
            }

        # Заменяем количество
        if override_quantity:
            self.cart[cart_key]['quantity'] = override_quantity

        # Добавляем к существующим
        else:
            self.cart[cart_key]['quantity'] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, product_size):
        product_id = str(product.id)
        size_id = str(product_size.id)
        cart_key = f"{product_id}_{size_id}"

        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def update_quantity(self, product, product_size, quantity):
        cart_key = f"{product.id}_{product_size.id}"

        if cart_key in self.cart:
            if quantity > 0:
                self.cart[cart_key]['quantity'] = quantity
            else:
                del self.cart[cart_key]
            self.save()

    def __iter__(self):
        from products.models import Product, ProductSize
        from decimal import Decimal
        
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {product.id: product for product in products}
        
        size_ids = [item['size_id'] for item in self.cart.values()]
        sizes = ProductSize.objects.filter(id__in=size_ids)
        size_dict = {size.id: size for size in sizes}
        
        for item in self.cart.values():
        
            enriched_item = item.copy()  
            
            product = product_dict.get(item['product_id'])
            product_size = size_dict.get(item['size_id'])
            
            if product and product_size:
                enriched_item['product'] = product
                enriched_item['size'] = product_size
                enriched_item['size_type_display'] = product_size.size.get_attribute_type_display()
                enriched_item['total_price'] = Decimal(item['price']) * item['quantity']
                yield enriched_item
            
    def __len__(self):

        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):

        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_items(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.save()


    def get_cart_items(self):
        return [
            {
                'product': item['product'],
                'product_name': item['product'].name,
                'product_slug': item['product'].slug,
                'size_display': item['size_type_display'],
                'size_value': item['size'].value,
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'total_price': item['total_price'],
                'cart_key': f"{item['product_id']}_{item['size_id']}"
            }
            for item in self
        ]
