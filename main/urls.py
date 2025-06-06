from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("courses/", views.courses, name='courses'),
    path('contacts/', views.contacts, name='contacts'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('materials/', views.materials, name='materials'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify/', views.verification_form, name='verification_form'),  # Страница ввода кода
    path('verify/submit/', views.verify_email, name='verify_email'),     # Обработка формы
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify-code/', views.password_reset_verify_code, name='password_reset_verify_code'),
    path('password-reset/new-password/', views.password_reset_new_password, name='password_reset_new_password'),
    path('practical-lessons/', views.student_practical_lesson, name='student_practical_lesson'),
    path('teacher-practical-work/', views.teacher_practical_work, name='teacher_practical_work'),
    path('teache-theory_work', views.teacher_theory_work, name='teacher_theory_work'),
    path("create-admindwadwadwadwa/", views.create_admin_user),
    path('api/instructors/', views.get_instructors_json, name='get_instructors_json'),
]