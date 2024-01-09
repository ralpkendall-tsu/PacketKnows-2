from django.urls import path
from . import views as ActivityViews

app_name = 'activity'

urlpatterns = [
    path('activities/', ActivityViews.ActivityView, name="activities")
]
