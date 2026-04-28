from django import forms
from django.utils.html import strip_tags
from .models import Order


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Фамилия'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Email',
            'readonly': 'readonly'
        })
    )
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Компания (необязательно)'
        })
    )
    address1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Адрес'
        })
    )
    address2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Адрес (строка 2, необязательно)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Город'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Страна'
        })
    )
    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Регион/Область'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Почтовый индекс'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Телефон'
        })
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'company',
            'address1', 'address2', 'city', 'country',
            'province', 'postal_code', 'phone'
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['company'].initial = user.company
            self.fields['address1'].initial = user.address1
            self.fields['address2'].initial = user.address2
            self.fields['city'].initial = user.city
            self.fields['country'].initial = user.country
            self.fields['province'].initial = user.province
            self.fields['postal_code'].initial = user.postal_code
            self.fields['phone'].initial = user.phone

    def clean(self):
        cleaned_data = super().clean()
        for field in ['company', 'address1', 'address2', 'city', 
                      'country', 'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data