from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import OTPCode, User
from .forms import UserChangeForm, UserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('phone',)
    list_display = ('phone', 'full_name', 'role', 'is_phone_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'is_phone_verified', 'is_staff', 'is_active')
    search_fields = ('phone', 'full_name', 'city', 'region')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal information', {'fields': ('full_name', 'role', 'city', 'region')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('phone', 'full_name', 'password1', 'password2', 'role')}),)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'purpose', 'created_at', 'expires_at', 'attempts', 'consumed_at')
    list_filter = ('purpose', 'consumed_at')
    search_fields = ('phone',)
    readonly_fields = ('phone', 'code_hash', 'purpose', 'registration_data', 'created_at', 'expires_at', 'attempts', 'consumed_at')
