from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Course)
admin.site.register(ActivityCategory)
admin.site.register(BaseActivity)
admin.site.register(Activity)