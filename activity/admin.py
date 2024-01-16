from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(ActivityCategory, ActivityCategoryAdmin)


class BaseActivityAdmin(admin.ModelAdmin):
    list_display = ('number', 'course', 'name', 'time_limit')
    search_fields = ('number', 'category__name', 'course__name')
    list_filter = ('category', 'course')

admin.site.register(BaseActivity, BaseActivityAdmin)


class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'base_activity_course_slug',
        'base_activity_number',
        'mode',
        'time_spent',
        'status',
    )
    list_filter = ('mode', 'status')
    search_fields = ('base_activity__course__slug', 'base_activity__number', 'id')

    def base_activity_course_slug(self, obj):
        return obj.base_activity.course.slug

    def base_activity_number(self, obj):
        return obj.base_activity.number

    base_activity_course_slug.short_description = 'Course Slug'
    base_activity_number.short_description = 'Base Activity Number'

admin.site.register(Activity, ActivityAdmin)