import secrets
import uuid
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import PendingUser, CustomUser
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
from django.core.exceptions import ObjectDoesNotExist


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
    subject = 'Ваш код подтверждения'
    plain_message = f'Ваш код подтверждения: {pending_user.verification_code}'
    html_message = f'''
        <p>Ваш код подтверждения:</p>
        <p style="font-size: 24px; font-weight: bold;">
            {pending_user.verification_code}
        </p>
    '''
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [pending_user.email],
        html_message=html_message,
        fail_silently=False,
    )


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']

            # Удаляем старую заявку, если такая есть (чтобы нельзя было спамить кодами)
            PendingUser.objects.filter(email=email).delete()

            # Создаём нового PendingUser
            pending_user = PendingUser.objects.create(
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number']
            )

            # Отправляем код на почту
            send_verification_email(pending_user)

            # Сохраняем email в сессии, но не создаём аккаунт сразу
            request.session['pending_email'] = email

            messages.success(request, "Код подтверждения отправлен на вашу почту.")
            return redirect('verification_form')  # Перенаправляем на ввод кода

        else:
            messages.error(request, "Ошибка при заполнении формы.")

    else:
        form = CustomUserCreationForm()

    return render(request, 'main/register.html', {'form': form})


def verify_email(request):
    email = request.session.get('pending_email')

    if not email:
        messages.error(request, "Сессия истекла. Пройдите регистрацию заново.")
        return redirect('register')

    if request.method == 'POST':
        if 'resend' in request.POST:  # Если нажали "Отправить снова"
            try:
                pending_user = PendingUser.objects.get(email=email)

                # Генерируем новый код подтверждения
                pending_user.verification_code = ''.join(secrets.choice('0123456789') for _ in range(5))
                pending_user.created_at = timezone.now()
                pending_user.save()

                # Отправляем новый код на почту
                send_verification_email(pending_user)
                messages.success(request, "Новый код отправлен на вашу почту.")

            except PendingUser.DoesNotExist:
                messages.error(request, "Ошибка! Пользователь не найден.")
                return redirect('register')

            return redirect('verification_form')

        else:  # Проверка введенного кода
            code = request.POST.get('code', '').strip()

            if not code.isdigit() or len(code) != 5:
                messages.error(request, "Код должен состоять из 5 цифр.")
                return redirect('verification_form')

            try:
                pending_user = PendingUser.objects.get(email=email, verification_code=code)
                # Проверяем срок действия кода (например, 60 минут)
                expiration_time = pending_user.created_at + timedelta(minutes=60)
                if timezone.now() > expiration_time:
                    pending_user.delete()
                    messages.error(request, "Срок действия кода истёк, пройдите регистрацию заново.")
                    return redirect('verification_form')

                # Создаём пользователя
                user = CustomUser.objects.create_user(
                    username=pending_user.email,
                    password=pending_user.password
                )

                UserProfile.objects.create(
                    user=user,
                    first_name=pending_user.first_name,
                    last_name=pending_user.last_name,
                    phone_number=pending_user.phone_number
                )

                # Удаляем временные данные
                pending_user.delete()
                del request.session['pending_email']

                login(request, user)

                return redirect('home')

            except PendingUser.DoesNotExist:
                messages.error(request, "Неверный код подтверждения.")
                return redirect('verification_form')

    return render(request, 'main/verification_form.html', {'email': email})


def verification_form(request):
    email = request.session.get('pending_email')

    if not email:
        messages.error(request, "Сессия истекла. Пройдите регистрацию заново.")
        return redirect('register')

    return render(request, 'main/verification_form.html', {'email': email})
# Create your views here.
