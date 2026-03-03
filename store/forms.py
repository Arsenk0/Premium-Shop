from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Вкажіть вашу пошту (для відновлення пароля)')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class OrderCreateForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Номер телефону повинен бути у форматі: '+380999999999'. Від 9 до 15 цифр."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': '+380 99 999 99 99'})
    )
    
    city_ref = forms.CharField(widget=forms.HiddenInput(), required=False)
    warehouse_ref = forms.CharField(widget=forms.HiddenInput(), required=False)

    contact_method = forms.ChoiceField(
        choices=[('TELEGRAM', 'Telegram'), ('INSTAGRAM', 'Instagram'), ('PHONE', 'Дзвінок по телефону')],
        initial='TELEGRAM',
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'contact_method', 'social_handle', 'city', 'city_ref', 'warehouse', 'warehouse_ref']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Олександр'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Шевченко'}),
            'social_handle': forms.TextInput(attrs={'placeholder': '@username або посилання'}),
            'city': forms.TextInput(attrs={'placeholder': 'Почніть вводити місто...', 'autocomplete': 'off'}),
            'warehouse': forms.Select(attrs={'disabled': 'disabled'}),
        }
        help_texts = {
            'social_handle': 'Вкажіть ваш Instagram або Telegram. Якщо ви обрали "Дзвінок", це поле можна залишити порожнім.',
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise forms.ValidationError("Ім'я занадто коротке")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise forms.ValidationError("Прізвище занадто коротке")
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Clean from spaces, dashes, etc.
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        if len(phone) < 10:
             raise forms.ValidationError("Введіть коректний номер телефону (напр. +380...)")
        return phone

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city or len(city) < 2:
            raise forms.ValidationError("Будь ласка, вкажіть місто")
        return city

    def clean_warehouse(self):
        warehouse = self.cleaned_data.get('warehouse')
        if not warehouse:
            raise forms.ValidationError("Будь ласка, оберіть відділення")
        return warehouse

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('contact_method')
        handle = cleaned_data.get('social_handle')

        if method in ['TELEGRAM', 'INSTAGRAM'] and handle:
            handle = handle.strip().rstrip('/')
            if handle.startswith('https://'):
                # Extract handle from link if possible
                handle = '@' + handle.split('/')[-1]
            elif not handle.startswith('@'):
                if handle.replace('.', '').replace('_', '').isalnum():
                    handle = '@' + handle
                else:
                    raise forms.ValidationError({'social_handle': f"Для {method} нікнейм зазвичай починається з @"})
            cleaned_data['social_handle'] = handle
        elif method == 'PHONE':
            cleaned_data['social_handle'] = cleaned_data.get('phone')
        return cleaned_data
