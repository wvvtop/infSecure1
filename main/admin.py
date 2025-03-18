from django.contrib import admin
from .models import CustomUser, UserProfile, PendingUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active')  # Только те поля, которые есть в модели
    list_filter = ('is_active',)  # Только те поля, которые есть в модели
    search_fields = ('username',)  # Только те поля, которые есть в модели
    ordering = ('username',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone_number')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('user__is_active',)


@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке записей
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'verification_code', 'created_at')

    # Добавляем фильтрацию по полям
    list_filter = ('created_at', 'first_name', 'last_name')

    # Добавляем возможность поиска по этим полям
    search_fields = ('email', 'first_name', 'last_name')

    # Ограничиваем количество записей на одной странице
    list_per_page = 20

    # Сортировка записей по умолчанию
    ordering = ('created_at',)

    # Сортировка по дате
    date_hierarchy = 'created_at'