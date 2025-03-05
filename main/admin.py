from django.contrib import admin
from .models import CustomUser, UserProfile

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