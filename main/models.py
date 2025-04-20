import secrets
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model

from project1 import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:    
            raise ValueError('У пользователя должен быть email!')
        username = self.normalize_email(username)  # Приводим email к нижнему регистру
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[EmailValidator(message="Введите корректный email-адрес.")]
    )
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)  # Новое поле
    is_student = models.BooleanField(default=False)  # Новое поле

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # Теперь username — это email

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=5, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.verification_code:
            while True:
                code = ''.join(secrets.choice('0123456789') for _ in range(5))
                if not PendingUser.objects.filter(verification_code=code).exists():
                    self.verification_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PasswordResetCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(secrets.choice('0123456789') for _ in range(5))
        super().save(*args, **kwargs)

    def is_valid(self):
        # Изменяем с 3600 (1 час) на 600 (10 минут)
        return (timezone.now() - self.created_at).total_seconds() < 600 and not self.is_used


class Exams(models.Model):
    user = models.OneToOneField(
        get_user_model(),  # Связь с CustomUser
        on_delete=models.CASCADE,  # Удаление при удалении пользователя
        related_name='exams'  # Доступ через user.exams
    )
    first_test = models.BooleanField(default=False)
    second_test = models.BooleanField(default=False)
    third_test = models.BooleanField(default=False)
    fourth_test = models.BooleanField(default=False)
    exam = models.BooleanField(default=False)

    def __str__(self):
        return f"Результаты экзаменов для {self.user.username}"

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"


class Practice(models.Model):
    teacher = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='practice_teacher'
    )
    date_of_lesson = models.DateField()
    time_of_lesson = models.TimeField()
    student = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practice_student'
    )

    class Meta:
        verbose_name = "Практика"
        verbose_name_plural = "Практика"
        unique_together = ('teacher', 'date_of_lesson', 'time_of_lesson')
        ordering = ['date_of_lesson', 'time_of_lesson']

    def __str__(self):
        return f"{self.teacher} – {self.date_of_lesson} {self.time_of_lesson}"