from django.contrib import admin
from .models import *

# Register your models here.
class TestReactivationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'message')
    search_fields = ('activity__base_activity__course__name', 'message')
    list_filter = ('activity__base_activity__number',)

admin.site.register(TestReactivation, TestReactivationAdmin)


class StudentIDChangeAdmin(admin.ModelAdmin):
    list_display = ('student', 'new_school_id')
    search_fields = ('student__email', 'new_school_id')
    list_filter = ('new_school_id',)
    
admin.site.register(StudentIDChange, StudentIDChangeAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'title', 'created_at')
    search_fields = ('sender__email', 'receiver__email', 'title')
    list_filter = ('created_at',)
    
admin.site.register(Notification, NotificationAdmin)