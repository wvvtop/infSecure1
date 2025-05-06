import secrets
from collections import defaultdict, Counter
from zoneinfo import ZoneInfo
from django.db import IntegrityError
import requests
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import PendingUser, CustomUser, PasswordResetCode, Exams, Practice
from django.utils import timezone
from datetime import timedelta, datetime, date, time
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileEditForm
from django.utils.timezone import now, make_aware
from axes.models import AccessAttempt
from django.contrib.auth import get_backends
from axes.handlers.proxy import AxesProxyHandler
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q, Count


def anonymous_required(view_function):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # или любой другой путь
        return view_function(request, *args, **kwargs)
    return wrapper


def teacher_required(view_function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher:
            return redirect('home')
        return view_function(request, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, "main/home.html")


def about(request):
    # Получаем всех активных пользователей с флагом is_teacher=True
    instructors = CustomUser.objects.filter(
        is_teacher=True,
        is_active=True
    ).select_related('profile')  # Используем select_related для оптимизации запросов

    context = {
        'instructors': instructors
    }
    return render(request, 'main/about.html', context)



def courses(request):
    return render(request, "main/courses.html")


def contacts(request):
    return render(request, "main/contacts.html")


def materials(request):
    return render(request, 'main/ticketsPDD.html')


@login_required(login_url="login")
def profile_view(request):
    return render(request, 'main/profile.html')


@login_required(login_url="login")
@teacher_required
def teacher_theory_work(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        exam_field = request.POST.get('exam_field')
        value = request.POST.get('value') == '1'

        if student_id and exam_field:
            try:
                student = CustomUser.objects.get(id=student_id)
                exam, created = Exams.objects.get_or_create(user=student)
                setattr(exam, exam_field, value)
                exam.save()
                return JsonResponse({'success': True})
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Студент не найден'})
        else:
            return JsonResponse({'success': False, 'error': 'Неверные данные'})

    # GET-запрос — обычный рендер страницы
    search_query = request.GET.get('search', '')
    students_list = CustomUser.objects.filter(is_student=True) \
        .select_related('profile', 'exams') \
        .order_by('profile__last_name', 'profile__first_name')

    if search_query:
        students_list = students_list.filter(
            Q(profile__first_name__icontains=search_query) |
            Q(profile__last_name__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    paginator = Paginator(students_list, 20)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, "main/teacherTheoryWork.html", context)


@login_required(login_url="login")
def student_practical_lesson(request):
    if not request.user.is_student:
        return redirect("home")

    exams, created = Exams.objects.get_or_create(user=request.user)
    completed_tests = sum([exams.first_test, exams.second_test, exams.third_test, exams.fourth_test])

    context = {
        'exams': exams,
        'completed_tests': completed_tests,
        'progress_width': completed_tests * 25,  # Считаем процент прямо во view
        'show_extra_functionality': completed_tests >= 3
    }
    return render(request, "main/practicalLesson.html", context)


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


@anonymous_required
def login_view(request):
    # Проверяем блокировку при любом запросе (GET или POST)
    username = request.POST.get('username', '').strip() if request.method == 'POST' else ''
    ip_address = request.META.get('REMOTE_ADDR')
    
    if AxesProxyHandler.is_locked(request):
        # Находим последнюю попытку входа с этого IP
        ip_attempt = AccessAttempt.objects.filter(ip_address=request.META.get('REMOTE_ADDR')).order_by(
            '-attempt_time').first()

        if ip_attempt:
            lockout_time = ip_attempt.attempt_time + timedelta(seconds=30)  # Время блокировки
            remaining_time = max(0, int((lockout_time - now()).total_seconds()))  # Сколько секунд осталось

        messages.error(request, f"⏳ Вход в учетную запись заблокирован: {remaining_time} сек.")
        return render(request, 'main/login.html', {'form': AuthenticationForm(), 'lockout_time': remaining_time})

    # Проверяем блокировку по IP и username
    is_locked = AxesProxyHandler.is_locked(request, credentials={'username': username}) if username else False

    # Если есть блокировка - показываем сообщение
    if is_locked:
        attempt = AccessAttempt.objects.filter(
            username=username if username else None,
            ip_address=ip_address
        ).order_by('-attempt_time').first()

        if attempt:
            lockout_time = attempt.attempt_time + timedelta(seconds=30)
            remaining_time = max(0, int((lockout_time - now()).total_seconds()))
            messages.error(request, f"⏳ Слишком много попыток! Попробуйте через {remaining_time} сек.")
            return render(request, 'main/login.html', {'form': AuthenticationForm(), 'lockout_time': remaining_time})

    # Обработка POST-запроса
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('home')

        # При любой ошибке делаем редирект, чтобы очистить POST-данные
        messages.error(request, "❌ Неверный логин или пароль")
        return redirect('login')

    # GET-запрос - показываем чистую форму
    return render(request, 'main/login.html', {'form': AuthenticationForm(), 'lockout_time': 0})


def custom_lockout(request, credentials=None, *args, **kwargs):
    username = credentials.get('username', '') if credentials else request.POST.get('username', '')
    remaining_time = 30  # Стандартное время блокировки

    if username:
        attempt = AccessAttempt.objects.filter(username=username).first()
        if attempt:
            lockout_time = attempt.attempt_time + timedelta(seconds=30)
            remaining_time = max(0, int((lockout_time - now()).total_seconds()))

    messages.error(request, f"⏳ Вход в учетную запись заблокирован: попробуйте через {remaining_time} сек.")
    return render(request, 'main/login.html', {'form': AuthenticationForm(), 'lockout_time': remaining_time})


def send_verification_email(pending_user):
    subject = 'Ваш код подтверждения'
    plain_message = (
        f'Здравствуйте!\n\n'
        f'Ваш код подтверждения: {pending_user.verification_code}\n\n'
        f'Если вы не запрашивали код, просто проигнорируйте это письмо.\n\n'
        f'С уважением,\nКоманда проекта.'
    )

    html_message = f'''
        <p>Здравствуйте!</p>
        <p>Ваш код подтверждения:</p>
        <p style="font-size: 24px; font-weight: bold;">{pending_user.verification_code}</p>
        <p>Если вы не запрашивали код, просто проигнорируйте это письмо.</p>
        <br>
        <p>С уважением,<br>Команда проекта.</p>
    '''

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [pending_user.email],
        html_message=html_message,
        fail_silently=False,
    )


@anonymous_required
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # Получаем ответ от hCaptcha
            captcha_response = request.POST.get('h-captcha-response')

            # Отправляем запрос на сервер hCaptcha для проверки
            captcha_verification_url = 'https://hcaptcha.com/siteverify'
            data = {
                'secret': settings.HCAPTCHA_SECRET_KEY,
                'response': captcha_response
            }
            response = requests.post(captcha_verification_url, data=data)
            result = response.json()
            print(result)
            # Если проверка hCaptcha прошла успешно
            if result.get('success'):
                email = form.cleaned_data['username']

                # Удаляем старую заявку, если такая есть
                PendingUser.objects.filter(email=email).delete()

                # Создаём нового PendingUser
                pending_user = PendingUser.objects.create(
                    email=email,
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    phone_number=form.cleaned_data['phone_number']
                )

                # Сохраняем email в сессии
                request.session['pending_email'] = email

                # Отправляем код на почту
                send_verification_email(pending_user)

                messages.success(request, "Код подтверждения отправлен на вашу почту.")
                return redirect('verification_form')  # Перенаправляем на ввод кода
            else:
                form.add_error(None, 'Ошибка проверки hCaptcha. Попробуйте снова.')

        # else:
        #     messages.error(request, "Ошибка при заполнении формы.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'main/register.html', {'form': form, "hcaptcha_site_key": settings.HCAPTCHA_SITE_KEY})


@anonymous_required
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

                # 🛠 Добавляем определение бэкенда перед login
                backend = get_backends()[0]  # Берем первый бэкенд из списка
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

                login(request, user)

                return redirect('home')

            except PendingUser.DoesNotExist:
                messages.error(request, "Неверный код подтверждения.")
                return redirect('verification_form')

    return render(request, 'main/verification_form.html', {'email': email})


@anonymous_required
def verification_form(request):
    email = request.session.get('pending_email')

    if not email:
        messages.error(request, "Сессия истекла. Пройдите регистрацию заново.")
        return redirect('register')

    return render(request, 'main/verification_form.html', {'email': email})


@anonymous_required
def password_reset_request(request):
    hcaptcha_site_key = settings.HCAPTCHA_SITE_KEY

    if request.method == 'POST':
        email = request.POST.get('email')

        # Проверка hCaptcha
        captcha_response = request.POST.get('h-captcha-response')
        if not captcha_response:
            messages.error(request, 'Пожалуйста, подтвердите, что вы не робот', extra_tags='captcha')
            return render(request, 'main/password_reset_request.html', {
                'hcaptcha_site_key': hcaptcha_site_key
            })

        # Валидация hCaptcha на сервере
        data = {
            'secret': settings.HCAPTCHA_SECRET_KEY,
            'response': captcha_response
        }
        response = requests.post('https://hcaptcha.com/siteverify', data=data)
        result = response.json()

        if not result.get('success'):
            messages.error(request, 'Ошибка проверки hCaptcha. Попробуйте снова.', extra_tags='captcha')
            return render(request, 'main/password_reset_request.html', {
                'hcaptcha_site_key': hcaptcha_site_key
            })

        # Сохраняем email в сессии
        request.session['reset_email'] = email

        try:
            # Проверяем существование пользователя
            user = CustomUser.objects.get(username=email)

            # Удаляем старые коды сброса
            PasswordResetCode.objects.filter(user=user).delete()

            # Создаем новый код сброса
            reset_code = PasswordResetCode.objects.create(user=user)

            send_mail(
                    'Сброс пароля - Автошкола Онлайн',
                    f'Ваш код для сброса пароля: {reset_code.code}\nКод действителен 10 минут.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
            )


            # Перенаправляем на страницу ввода кода
            return redirect('password_reset_verify_code')

        except CustomUser.DoesNotExist:
            # В production не сообщаем, что пользователя нет
            if settings.DEBUG:
                print(f"Попытка сброса пароля для несуществующего email: {email}")

            # Все равно перенаправляем на страницу ввода кода (security through obscurity)
            return redirect('password_reset_verify_code')

    # GET запрос - отображаем форму
    return render(request, 'main/password_reset_request.html', {
        'hcaptcha_site_key': hcaptcha_site_key
    })


@anonymous_required
def password_reset_verify_code(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')

    if request.method == 'POST':
        code = request.POST.get('code')

        # Пытаемся найти пользователя
        try:
            user = CustomUser.objects.get(username=email)
            reset_code = PasswordResetCode.objects.filter(user=user, code=code).first()

            if reset_code and reset_code.is_valid():
                reset_code.is_used = True
                reset_code.save()
                request.session['reset_user_id'] = user.id
                return redirect('password_reset_new_password')
            else:
                # Общее сообщение без деталей
                messages.error(request, 'Неверный код')
        except CustomUser.DoesNotExist:
            # Показываем такое же сообщение, как при неверном коде
            messages.error(request, 'Неверный код')

    return render(request, 'main/password_reset_verify_code.html', {'email': email})


@anonymous_required
def password_reset_new_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_request')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('password_reset_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
        else:
            user.set_password(new_password)
            user.save()

            # Очищаем сессию
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']

            messages.success(request, 'Пароль успешно изменен. Теперь вы можете войти с новым паролем.')
            return redirect('login')

    return render(request, 'main/password_reset_new_password.html')


#Работа инструктора
TIME_SLOTS = [
    ('08:30', '8:30'),
    ('10:15', '10:15'),
    ('12:00', '12:00'),
    ('14:10', '14:10'),
    ('15:55', '15:55'),
    ('17:40', '17:40'),
]


def send_cancellation_email(practice):
    student = practice.student
    subject = 'Отмена занятия по вождению'
    message = (
        f'Здравствуйте, {student.profile.first_name}!\n\n'
        f'Ваше занятие с инструктором {practice.teacher.profile.first_name + " " + practice.teacher.profile.last_name} '
        f'на {practice.date_of_lesson.strftime("%d.%m.%Y")} в {practice.time_of_lesson} было отменено.\n\n'
        'Пожалуйста, выберите другое время или другого инструктора.\n\n'
        'С уважением,\n'
        'Автошкола'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.username],
        fail_silently=False
    )


def get_russian_weekday(date_obj):
    weekdays = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }
    return weekdays[date_obj.weekday()]


@login_required(login_url="login")
@teacher_required
def teacher_practical_work(request):
    # if not request.user.is_teacher:
    #     return redirect('home')

        # Активируем нужный часовой пояс
    tz = ZoneInfo(settings.TIME_ZONE)
    timezone.activate(tz)

    # Получаем текущее время с учетом часового пояса
    _now = timezone.localtime(timezone.now())
    today = _now.date()
    current_week_start = today - timedelta(days=today.weekday())

    # Обработка POST-запроса
    if request.method == 'POST' and 'update_schedule' in request.POST:
        week_offset = int(request.POST.get('week_offset', 0))
        selected_week_start = current_week_start + timedelta(weeks=week_offset)
        selected_slots = request.POST.getlist('time_slots')

        # Получаем ВСЕ существующие занятия на эту неделю
        existing_practices = Practice.objects.filter(
            teacher=request.user,
            date_of_lesson__gte=selected_week_start,
            date_of_lesson__lte=selected_week_start + timedelta(days=6)
        )

        # Создаем список уже занятых слотов в формате "2025-04-21_08:30"
        existing_slot_keys = [
            f"{p.date_of_lesson}_{p.time_of_lesson.strftime('%H:%M')}"
            for p in existing_practices
        ]

        # 1. Создаем только НОВЫЕ слоты (которых еще нет)
        for slot_key in selected_slots:
            if slot_key not in existing_slot_keys:  # Если такого слота нет в базе
                date_str, time_str = slot_key.split('_')
                try:
                    Practice.objects.create(
                        teacher=request.user,
                        date_of_lesson=date.fromisoformat(date_str),
                        time_of_lesson=time_str,
                        student=None
                    )
                except IntegrityError:
                    continue  # На случай редких коллизий

        # 2. Удаляем слоты, которые СНЯЛИ галочкой
        for practice in existing_practices:
            practice_key = f"{practice.date_of_lesson}_{practice.time_of_lesson.strftime('%H:%M')}"
            if practice_key not in selected_slots:  # Если галочку сняли
                if practice.student:  # Если студент записан - отправляем уведомление
                    send_cancellation_email(practice)
                practice.delete()  # Удаляем занятие

        return redirect(request.get_full_path())

    # Обработка GET-запроса
    week_offset = max(0, int(request.GET.get('week', 0)))  # Не позволяем выбрать прошедшие недели
    selected_week_start = current_week_start + timedelta(weeks=week_offset)

    # Ограничиваем просмотр 3 неделями вперед
    max_week_start = current_week_start + timedelta(weeks=3)
    if selected_week_start > max_week_start:
        selected_week_start = max_week_start
        week_offset = 3

    # Создаем список дней для выбранной недели
    week_days = []
    for i in range(7):
        day = selected_week_start + timedelta(days=i)
        week_days.append(day)

    # Получаем занятия для отображения
    practices = Practice.objects.filter(
        teacher=request.user,
        date_of_lesson__gte=selected_week_start,
        date_of_lesson__lte=selected_week_start + timedelta(days=6)
    ).order_by('date_of_lesson', 'time_of_lesson')

    # Формируем расписание
    schedule = []
    for day in week_days:
        day_schedule = {
            'date': day,
            'day_name': get_russian_weekday(day),
            'slots': []
        }

        for time_slot in TIME_SLOTS:
            slot_value, slot_display = time_slot
            practice_exists = practices.filter(
                date_of_lesson=day,
                time_of_lesson=slot_value
            ).exists()

            practice_with_student = practices.filter(
                date_of_lesson=day,
                time_of_lesson=slot_value,
                student__isnull=False
            ).first()

            day_schedule['slots'].append({
                'time': slot_display,
                'value': slot_value,
                'exists': practice_exists,
                'has_student': practice_with_student is not None,
                'practice_id': practice_with_student.id if practice_with_student else None
            })

        schedule.append(day_schedule)

    # Подготовка данных для вкладки студентов
    upcoming_practices = Practice.objects.filter(
        teacher=request.user,
        date_of_lesson__gte=today,
        student__isnull=False
    ).order_by('date_of_lesson', 'time_of_lesson')

    practices_by_day = {}
    for practice in upcoming_practices:
        if practice.date_of_lesson not in practices_by_day:
            practices_by_day[practice.date_of_lesson] = []
        practices_by_day[practice.date_of_lesson].append(practice)

    sorted_days = sorted(practices_by_day.keys())
    today_practices = practices_by_day.get(today, [])
    other_days = [(day, practices_by_day[day]) for day in sorted_days if day != today]

    context = {
        'schedule': schedule,
        'current_week_start': selected_week_start,
        'current_week_end': selected_week_start + timedelta(days=6),
        'week_offset': week_offset,
        'max_week_offset': 3,
        'today': today,
        'today_practices': today_practices,
        'other_days': other_days,
        'active_tab': request.GET.get('tab', 'schedule')
    }

    return render(request, 'main/teacher_practical_work.html', context)
#Конец работы инструктора


# tz = ZoneInfo(settings.TIME_ZONE)
# timezone.activate(tz)
# #Получаем текущее время с учетом часового пояса
# _now = timezone.localtime(timezone.now())
# today = _now.date()


#Работа студента
@login_required(login_url="login")
def student_practical_lesson(request):
    if not request.user.is_student:
        return redirect("home")

    # Установка часового пояса
    tz = ZoneInfo(settings.TIME_ZONE)
    timezone.activate(tz)
    _now = timezone.localtime(timezone.now())
    today = _now.date()
    max_date = today + timedelta(days=4)

    # Базовые данные (всегда получаем)
    exams, _ = Exams.objects.get_or_create(user=request.user)
    completed_tests = sum([exams.first_test, exams.second_test,
                           exams.third_test, exams.fourth_test])

    # Базовый контекст
    context = {
        'exams': exams,
        'completed_tests': completed_tests,
        'progress_width': completed_tests * 25,
        'show_extra_functionality': completed_tests >= 3,
        'today': today,
        'now': _now,
    }

    # Если тестов меньше 3 - возвращаем сразу
    if completed_tests < 3:
        return render(request, "main/practicalLesson.html", context)

    # Основная логика (только для 3+ тестов)
    current_bookings = (
        request.user.practice_student
        .filter(date_of_lesson__gte=today)
        .select_related('teacher', 'teacher__profile')
        .order_by('date_of_lesson', 'time_of_lesson')
    )

    # Подготовка данных о записях
    booked_slots = set()
    bookings_per_day = defaultdict(int)

    for booking in current_bookings:
        slot_key = (booking.date_of_lesson, booking.time_of_lesson)
        booked_slots.add(slot_key)
        bookings_per_day[booking.date_of_lesson] += 1

    full_days = {date for date, count in bookings_per_day.items() if count >= 2}

    # Обработка POST-запросов
    if request.method == 'POST':
        action = request.POST.get('action')
        slot_id = request.POST.get('slot_id')

        if action == 'cancel':
            try:
                slot = Practice.objects.get(id=slot_id, student=request.user)
                lesson_datetime = timezone.make_aware(
                    datetime.combine(slot.date_of_lesson, slot.time_of_lesson))

                if (lesson_datetime - _now) > timedelta(hours=2):
                    slot.student = None
                    slot.save()
                    messages.success(request, 'Запись успешно отменена!')
                else:
                    messages.error(request, 'Отмена возможна только за 2+ часа до занятия')
            except Practice.DoesNotExist:
                messages.error(request, 'Запись не найдена')

            return redirect('student_practical_lesson')

        elif not action:  # Новая запись
            try:
                slot = Practice.objects.get(id=slot_id, student__isnull=True)

                if bookings_per_day.get(slot.date_of_lesson, 0) >= 2:
                    messages.error(request, f'Лимит 2 занятий в день ({slot.date_of_lesson.strftime("%d.%m.%Y")})')
                elif (slot.date_of_lesson, slot.time_of_lesson) in booked_slots:
                    messages.error(request, 'Вы уже записаны на это время')
                elif not slot.is_available:
                    messages.error(request, 'Запись возможна только за 2+ часа до занятия')
                else:
                    slot.student = request.user
                    slot.save()

                return redirect('student_practical_lesson')
            except Practice.DoesNotExist:
                messages.error(request, 'Время уже занято')

    # Получение доступных слотов
    available_slots = (
        Practice.objects
        .filter(
            student__isnull=True,
            date_of_lesson__range=[today, max_date]
        )
        .exclude(date_of_lesson__in=full_days)
        .select_related('teacher', 'teacher__profile')
        .order_by('date_of_lesson', 'time_of_lesson')
    )

    # Фильтрация уже занятых слотов
    available_slots = [
        slot for slot in available_slots
        if (slot.date_of_lesson, slot.time_of_lesson) not in booked_slots
    ]

    # Добавляем дополнительные данные в контекст
    context.update({
        'current_bookings': current_bookings,
        'available_slots': available_slots,
        'max_date': max_date,
        'booked_slots': booked_slots,
        'full_days': full_days,
    })

    return render(request, "main/practicalLesson.html", context)

# Create your views here.
