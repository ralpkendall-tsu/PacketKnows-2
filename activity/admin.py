from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(ActivityCategory)
admin.site.register(BaseActivity)
admin.site.register(Activity)