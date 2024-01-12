from django.urls import path
from . import views as activityViews

app_name = 'activity'

urlpatterns = [
    path('activities/', activityViews.ActivityView, name="activities"),
    path('update-chart-data/<str:mode>/', activityViews.update_chart_data, name='updateChartData'),
    path('activity-options/', activityViews.ActivityOptions, name='activityOptions'),
     path('serve-pdf/<path:pdf_path>/', activityViews.serve_pdf, name='servePdf'),
]
