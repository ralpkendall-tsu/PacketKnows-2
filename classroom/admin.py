from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'instructor', 'is_active',)
    list_filter = ('course', 'is_active', 'date_updated',)
    search_fields = ('name', 'code', 'instructor__email',)
    
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_full_name', 'classroom', 'status', 'date_updated')
    search_fields = ('student__first_name', 'student__last_name', 'classroom__name')
    list_filter = ('status', 'date_updated')
    
    def student_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_full_name.short_description = 'Student'

admin.site.register(Enrollment, EnrollmentAdmin)