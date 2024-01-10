from django.urls import path
from . import views as coreViews

app_name = 'core'

urlpatterns = [
    path('', coreViews.LandingPageView, name='landingPage'),
    path('dashboard/', coreViews.DashboardView, name='dashboard'),
    path('classes/', coreViews.ClassesView, name='classes'),
    path('settings/', coreViews.SettingsView, name='settings'),
    path('help/', coreViews.HelpView, name='help'),
    path('progress-report/<slug:classSlug>/training/', coreViews.ProgressReportTrainingView, name='progressReportTraining'),
    path('progress-report/<slug:classSlug>/testing/', coreViews.ProgressReportTestingView, name='progressReportTesting'),
    path('exam-list/<slug:classSlug>/<str:mode>/', coreViews.ExamListView, name='examList'),
    path('activity/<int:id>/<str:mode>/', coreViews.ActivitySimulationView, name='activity'),
    path('progress-report-instructor/<slug:classSlug>/<int:userID>/training/', coreViews.ProgressReportTrainingInstructorView, name='progressReportTrainingInstructor'),
    path('progress-report-instructor/<slug:classSlug>/<int:userID>/testing/', coreViews.ProgressReportTestingInstructorView, name='progressReportTestingInstructor'),
]
