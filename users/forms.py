from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Фамилия'
        })
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Подтвердите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Пароль'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный email или пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт неактивен.')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(
            r'^\+?7?\d{10,15}$', "Введите корректный номер телефона.")],
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Телефон'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Фамилия'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
            'placeholder': 'Email'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company',
                  'address1', 'address2', 'city', 'country',
                  'province', 'postal_code', 'phone')
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Компания'
            }),
            'address1': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Адрес'
            }),
            'address2': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Адрес (строка 2)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Город'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Страна'
            }),
            'province': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Регион'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full border border-pottery/30 rounded-lg py-2.5 px-4 text-sm text-stone placeholder-stone/50 focus:outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta transition-colors bg-cream/50',
                'placeholder': 'Почтовый индекс'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and User.objects.filter(phone=phone).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(
                'Этот номер телефона уже используется.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email
        for field in ['company', 'address1', 'address2', 'city', 'country',
                      'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data
