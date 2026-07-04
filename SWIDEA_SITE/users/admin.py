from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname',)}),
    )
    list_display = ('username', 'nickname', 'email', 'is_staff')


admin.site.register(CustomUser, CustomUserAdmin)