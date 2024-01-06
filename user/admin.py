from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserCategory

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'category', 'school_id', 'icon', 'evidences')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff', 'category', 'school_id', 'evidences'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserCategory)
