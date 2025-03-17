import uuid
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification, PendingUser, CustomUser
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileEditForm
from django.contrib.sites.shortcuts import get_current_site


def home(request):
    return render(request, "main/home.html")

def about(request):
    return render(request, "main/about.html")

def courses(request):
    return render(request, "main/courses.html")

def contacts(request):
    return render(request, "main/contacts.html")

def login_page(request):
    return render(request, "main/login.html")

# def register(request):
#     return render(request, "main/register.html")

@login_required
def profile_view(request):
    return render(request, 'main/profile.html')

def materials(request):
    return render(request, 'main/ticketsPDD.html')


@login_required
def edit_profile(request):
    profile = request.user.profile  # Получаем профиль текущего пользователя

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправляем на страницу профиля
    else:
        form = ProfileEditForm(instance=profile)

        # Устанавливаем текущие значения в placeholder
        form.fields['first_name'].widget.attrs.update({'placeholder': profile.first_name})
        form.fields['last_name'].widget.attrs.update({'placeholder': profile.last_name})
        form.fields['phone_number'].widget.attrs.update({'placeholder': profile.phone_number})

    return render(request, 'main/editProfile.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Замените 'home' на имя вашего URL
            else:
                messages.error(request, "Неправильная почта или пароль")
        else:
            messages.error(request, "Неправильная почта или пароль")
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def send_verification_email(pending_user):
    subject = 'Подтверждение регистрации'
    message = f'Для завершения регистрации перейдите по ссылке: {settings.BASE_URL}/verify/{pending_user.verification_code}/'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [pending_user.email],
        fail_silently=False,
    )


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Сохраняем данные в PendingUser
            pending_user = PendingUser.objects.create(
                email=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number']
            )

            # Отправляем письмо с кодом подтверждения
            send_verification_email(pending_user)

            # Перенаправляем на страницу с сообщением о отправке письма
            return redirect('email_sent')
        else:
            messages.error(request, "Ошибка при заполнении формы.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})


def verify_email(request, code):
    pending_user = get_object_or_404(PendingUser, verification_code=code)

    # Создаём пользователя в основной базе данных
    user = CustomUser.objects.create_user(
        username=pending_user.email,
        password=pending_user.password
    )

    # Создаём профиль пользователя
    profile = UserProfile.objects.create(
        user=user,
        first_name=pending_user.first_name,
        last_name=pending_user.last_name,
        phone_number=pending_user.phone_number
    )

    # Удаляем временные данные
    pending_user.delete()

    # Авторизуем пользователя
    login(request, user)

    # Перенаправляем на страницу успешной верификации
    return render(request, 'main/verification_success.html')


def email_sent(request):
    return render(request, 'main/email_sent.html')
# Create your views here.
