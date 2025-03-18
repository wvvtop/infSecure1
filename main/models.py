import secrets
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import EmailValidator


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