from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, ClientProfile, Portfolio


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'user_type', 'is_verified',
        'is_staff', 'is_active', 'date_joined'
    )
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace Info', {
            'fields': ('user_type', 'is_verified', 'profile_image')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Marketplace Info', {
            'fields': ('user_type', 'is_verified')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'university', 'degree', 'experience_level',
        'is_available', 'is_verified'
    )
    list_filter = ('experience_level', 'is_available', 'is_verified')
    search_fields = ('user__username', 'university', 'skills')


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'business_type')
    search_fields = ('user__username', 'company_name', 'business_type')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'freelancer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'freelancer__username')
