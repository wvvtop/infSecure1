"""
Django settings for project1 project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import json
from pathlib import Path


#host = "http://localhost:8000"
host = "192.168.138.51"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)b*sav!dbpr0=zvz5r#52_n6@#srj_wmzv%zglflixg+^vtran'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["192.168.138.51", "127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    "main",
    "hcaptcha",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project1.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'driving_school',
        'USER': 'driving_school_admin',
        'PASSWORD': 'admin1234',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'school_user': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'driving_school',
        'USER': 'driving_school_user',
        'PASSWORD': 'qwerty1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'main.CustomUser'
LOGOUT_REDIRECT_URL = 'home'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Krasnoyarsk'

USE_I18N = True

USE_TZ = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'  # SMTP-сервер Yandex
EMAIL_PORT = 465  # Порт для SSL
EMAIL_USE_SSL = True  # Использовать SSL
# EMAIL_PORT = 587  # Порт для TLS
# EMAIL_USE_TLS = True  # Использовать TLS (если используете порт 587)

with open('settings.json') as f:
    templates = json.load(f)

EMAIL_HOST_USER = templates.get("email")  # Ваш полный email-адрес
EMAIL_HOST_PASSWORD = templates.get("passwordEmail")  # Пароль от Yandex или пароль приложения

DEFAULT_FROM_EMAIL = templates.get("email")  # Email, который будет указан как отправитель

BASE_URL = host

BACKGROUND_TASK_RUN_ASYNC = True

HCAPTCHA_SITE_KEY = templates.get("site_key")    #sitekey
HCAPTCHA_SECRET_KEY = templates.get("secret_key")   #secretkey


