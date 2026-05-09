from django import forms
from django.utils.html import strip_tags
from .models import Order


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Фамилия'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Email',
        })
    )
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Компания (необязательно)'
        })
    )
    address1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Адрес'
        })
    )
    address2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Адрес (строка 2, необязательно)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Город'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Страна'
        })
    )
    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Регион/Область'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Почтовый индекс'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-full',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Телефон'
        })
    )
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full py-2 px-3 text-sm focus:outline-none transition-all rounded-lg',
            'style': 'border: 1px solid #E8E2D9; color: #4A3B32; font-family: "Chiron GoRound TC", "Inter", sans-serif; background-color: white;',
            'placeholder': 'Особые пожелания...',
            'rows': 3
        })
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'company',
            'address1', 'address2', 'city', 'country',
            'province', 'postal_code', 'phone', 'special_instructions'
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
        # Убираем readonly с email
        self.fields['email'].widget.attrs.pop('readonly', None)

    def clean(self):
        cleaned_data = super().clean()
        for field in ['company', 'address1', 'address2', 'city', 
                      'country', 'province', 'postal_code', 'phone', 'special_instructions']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data