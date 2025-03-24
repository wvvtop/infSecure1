from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .validators import validate_password_complexity
from .models import CustomUser, UserProfile
# forms.py
from django import forms
from .models import UserProfile
from django.core.exceptions import ValidationError


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone_number'].label = 'Номер телефона'


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(
        max_length=12,
        required=True,
        validators=[RegexValidator(
            regex=r'^\+7\d{10}$',
            message="Введите номер в формате +7 (999) 999 9999"
        )]
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'phone_number')

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password_complexity(password1)  # Применяем кастомный валидатор
        return password1