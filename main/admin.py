from django.contrib import admin
from .models import CustomUser, UserProfile, PendingUser, PasswordResetCode


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_teacher', 'is_student', 'is_admin')
    list_filter = ('is_active', 'is_teacher', 'is_student', 'is_admin')
    search_fields = ('username',)
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_teacher', 'is_student'),
        }),
    )


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


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'code')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def is_valid(self, obj):
        return obj.is_valid()

    is_valid.boolean = True
    is_valid.short_description = 'Действителен'
