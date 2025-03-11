from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
# from .forms import CustomUserCreationForm
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

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



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"Пользователь создан: {user.username}")  # Отладочное сообщение
            profile = UserProfile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number']
            )
            print(f"Профиль создан: {profile}")  # Отладочное сообщение

            # Автоматический логин сразу после регистрации
            login(request, user)

            return redirect('home')  # Перенаправляем на главную или куда нужно
        else:
            print("Форма не валидна")  # Отладочное сообщение
            print(form.errors)  # Вывод ошибок формы
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

# Create your views here.
