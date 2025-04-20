from django.contrib import admin
from .models import CustomUser, UserProfile, PendingUser, PasswordResetCode, Exams, Practice


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

    actions = ['make_student', 'make_teacher']
    # Кастомные методы для красивого отображения
    def is_student_display(self, obj):
        return obj.is_student

    is_student_display.boolean = True
    is_student_display.short_description = 'Студент'

    def is_admin_display(self, obj):
        return obj.is_admin

    is_admin_display.boolean = True
    is_admin_display.short_description = 'Админ'

    def has_exams_record(self, obj):
        return hasattr(obj, 'exams')

    has_exams_record.boolean = True
    has_exams_record.short_description = 'Запись Exams'

    # Действие "Сделать студентом"
    def make_student(self, request, queryset):
        # Обновляем статус и создаем Exams
        updated_users = queryset.update(is_student=True, is_teacher=False)

        # Создаем записи Exams для тех, у кого их нет
        created_records = 0
        for user in queryset:
            _, created = Exams.objects.get_or_create(user=user)
            if created:
                created_records += 1

        self.message_user(
            request,
            f"Обновлено {updated_users} пользователей. Создано {created_records} записей Exams."
        )

    make_student.short_description = "Сделать выбранных студентами (+Exams)"

    # Действие "Сделать преподавателем"
    def make_teacher(self, request, queryset):
        queryset.update(is_teacher=True, is_student=False)
        self.message_user(request, f"{queryset.count()} пользователей теперь преподаватели")

    make_teacher.short_description = "Сделать выбранных преподавателями"

    # Опционально: подтверждение действия
    def render_change_form(self, request, context, *args, **kwargs):
        context.update({'show_save_and_continue': False})
        return super().render_change_form(request, context, *args, **kwargs)



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


@admin.register(Exams)
class ExamsAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_test', 'second_test', 'third_test', 'fourth_test', 'exam')
    list_filter = ('first_test', 'second_test', 'third_test', 'fourth_test', 'exam')
    search_fields = ('user__username',)
    list_editable = ('first_test', 'second_test', 'third_test', 'fourth_test', 'exam')
    ordering = ('user',)  # Сортировка по пользователю

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Результаты тестов', {
            'fields': ('first_test', 'second_test', 'third_test', 'fourth_test')
        }),
        ('Экзамен', {
            'fields': ('exam',)
        }),
    )


@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date_of_lesson', 'time_of_lesson', 'student')
    list_filter = ('date_of_lesson', 'teacher')
    search_fields = ('teacher__username', 'student__username')
