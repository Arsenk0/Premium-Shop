from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Order, Review, Profile


class UserSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text=_('Вкажіть вашу пошту (для відновлення пароля)'),
        error_messages={
            'required': _("Будь ласка, введіть вашу електронну пошту."),
            'invalid': _("Введіть коректну адресу електронної пошти.")
        }
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages.update({
            'required': _("Будь ласка, введіть ім'я користувача."),
            'invalid': _("Логін може містити лише літери, цифри та символи @/./+/-/_"),
            'unique': _("Користувач із таким іменем вже існує. Будь ласка, оберіть інше."),
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and len(username) < 3:
            raise forms.ValidationError(_("Логін повинен містити щонайменше 3 символи."))
        # uniqueness is handled by model validation but we can return username
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Цей email вже використовується в системі. Можливо, ви вже зареєстровані?"))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        password_confirm = cleaned_data.get("password2")

        if password and password_confirm and password != password_confirm:
            self.add_error('password2', _("Паролі не співпадають. Будь ласка, перевірте введені дані."))
        return cleaned_data

class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Неправильний логін або пароль. Спробуйте ще раз."),
        'inactive': _("Цей акаунт деактивовано. Зверніться до служби підтримки."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages.update({
            'required': _("Будь ласка, введіть логін та пароль.")
        })
        self.fields['password'].error_messages.update({
            'required': _("Будь ласка, введіть логін та пароль.")
        })


class OrderCreateForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-]{9,20}$',
                message=_("Номер телефону повинен бути у форматі: '+380999999999'. Від 9 до 15 цифр.")
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': '+380 99 999 99 99'})
    )

    city_ref = forms.CharField(widget=forms.HiddenInput(), required=False)
    warehouse_ref = forms.CharField(widget=forms.HiddenInput(), required=False)

    contact_method = forms.ChoiceField(
        choices=[('TELEGRAM', 'Telegram'), ('INSTAGRAM', 'Instagram'), ('PHONE', _('Дзвінок по телефону'))],
        initial='TELEGRAM',
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'contact_method', 'social_handle', 'city', 'city_ref',
                  'warehouse', 'warehouse_ref']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('Олександр')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Шевченко')}),
            'social_handle': forms.TextInput(attrs={'placeholder': _('@username або посилання')}),
            'city': forms.TextInput(attrs={'placeholder': _('Почніть вводити місто...'), 'autocomplete': 'off'}),
            'warehouse': forms.Select(attrs={'disabled': 'disabled'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@mail.com'}),
        }
        help_texts = {
            'social_handle': _('Вкажіть ваш Instagram або Telegram. Якщо ви обрали "Дзвінок", це поле можна залишити порожнім.'),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise forms.ValidationError(_("Ім'я занадто коротке"))
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise forms.ValidationError(_("Прізвище занадто коротке"))
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        if len(phone) < 10:
            raise forms.ValidationError(_("Введіть коректний номер телефону (напр. +380...)"))
        return phone

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city or len(city) < 2:
            raise forms.ValidationError(_("Будь ласка, вкажіть місто"))
        return city

    def clean_warehouse(self):
        warehouse = self.cleaned_data.get('warehouse')
        if not warehouse:
            raise forms.ValidationError(_("Будь ласка, оберіть відділення"))
        return warehouse

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('contact_method')
        handle = cleaned_data.get('social_handle')

        if method in ['TELEGRAM', 'INSTAGRAM'] and handle:
            handle = handle.strip().rstrip('/')
            if handle.startswith('https://'):
                handle = '@' + handle.split('/')[-1]
            elif not handle.startswith('@'):
                if handle.replace('.', '').replace('_', '').isalnum():
                    handle = '@' + handle
                else:
                    raise forms.ValidationError({'social_handle': _("Для %(method)s нікнейм зазвичай починається з @") % {'method': method}})
            cleaned_data['social_handle'] = handle
        elif method == 'PHONE':
            cleaned_data['social_handle'] = cleaned_data.get('phone')
        return cleaned_data



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Ваш відгук...')}),
            'rating': forms.Select(attrs={'class': 'form-group'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Ім'я")}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Прізвище")}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _("Email")}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'social_handle', 'city', 'city_ref', 'warehouse', 'warehouse_ref']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Телефон")}),
            'social_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Нікнейм або номер")}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Місто"), 'id': 'city-search', 'autocomplete': 'off'}),
            'city_ref': forms.HiddenInput(),
            'warehouse': forms.Select(attrs={'class': 'form-control', 'id': 'warehouse-select'}),
            'warehouse_ref': forms.HiddenInput(),
        }
