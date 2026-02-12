from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'rut', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'rut', 'email']
    list_editable = ['is_active']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'company', 'role', 'is_active']
    list_filter = ['is_active', 'is_staff', 'groups', 'company']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['is_active']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'position', 'avatar')}),
        (_('Compañía'), {'fields': ('company',)}),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'company', 'groups'),
        }),
    )