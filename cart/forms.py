from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CartItem
from products.models import ProductSize

'''validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'w-16 text-center border border-pottery/30 rounded-lg py-2',
            'min': '1'
        })'''
class AddToCartForm(forms.Form):
    size_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1,
        validators=[MinValueValidator(1)],
    )
    '''widget=forms.RadioSelect(attrs={
                        'class': 'size-radio hidden',
                        'hx-trigger': 'change',
                        'hx-post': '.',
                        'hx-target': '#add-to-cart-form'
                    })'''
    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        
        if product:
            sizes = product.product_sizes.filter(stock__gt=0)
            if sizes.exists():
                self.fields['size_id'] = forms.ChoiceField(
                    choices=[(ps.id, self._get_size_display(ps)) for ps in sizes],
                    required=True,
                    initial=sizes.first().id,
                )
            else:
                self.fields['size_id'] = forms.ChoiceField(
                    choices=[('', 'Нет доступных размеров')],
                    required=False,
                    #widget=forms.Select(attrs={'disabled': 'disabled'})
                )
    
    def _get_size_display(self, product_size):
        size_attr = product_size.size
        return f"{size_attr.get_attribute_type_display()}: {product_size.value} ({product_size.stock} шт.)"
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.product:
            size_id = cleaned_data.get('size_id')
            quantity = cleaned_data.get('quantity', 1)
            
            if size_id:
                try:
                    product_size = self.product.product_sizes.get(id=size_id)
                    if product_size.stock < quantity:
                        self.add_error('quantity', 
                            f'Недостаточно товара. Доступно: {product_size.stock} шт.')
                except ProductSize.DoesNotExist:
                    self.add_error('size_id', 'Выбранный размер не существует')
        
        return cleaned_data


class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.product_size:
            max_stock = self.instance.product_size.stock
            self.fields['quantity'].validators.append(
                MaxValueValidator(max_stock)
            )
            self.fields['quantity'].widget = forms.NumberInput(attrs={
                'class': 'w-16 text-center border border-pottery/30 rounded-lg py-2',
                'min': '1',
                'max': max_stock,
                'hx-post': '.',
                'hx-trigger': 'change delay:500ms',
                'hx-target': '#cart-item-' + str(self.instance.id)
            })
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        max_stock = self.instance.product_size.stock
        
        if quantity > max_stock:
            raise forms.ValidationError(f'Недостаточно товара. Доступно: {max_stock} шт.')
        
        if quantity < 1:
            raise forms.ValidationError('Количество должно быть не менее 1')
        
        return quantity


class RemoveFromCartForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput())


'''class ApplyPromoForm(forms.Form):
    promo_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2 px-4 text-sm',
            'placeholder': 'Промокод'
        })
    )'''