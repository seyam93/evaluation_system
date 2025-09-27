from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'profile__user_type', 'profile__is_active_evaluator')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_user_type(self, obj):
        return obj.profile.get_user_type_display() if hasattr(obj, 'profile') else 'No Profile'
    get_user_type.short_description = 'User Type'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'department', 'employee_id', 'is_active_evaluator', 'created_at']
    list_filter = ['user_type', 'is_active_evaluator', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type')
        }),
        ('Professional Details', {
            'fields': ('employee_id', 'department', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active_evaluator',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
