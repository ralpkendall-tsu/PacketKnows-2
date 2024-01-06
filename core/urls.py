from django.urls import path
from . import views as coreViews

app_name = 'core'

urlpatterns = [
    path('', coreViews.LandingPageView, name='landingPage'),
    path('dashboard/', coreViews.DashboardView, name='dashboard'),
    path('classes/', coreViews.ClassesView, name='classes'),
    path('settings/', coreViews.SettingsView, name='settings'),
    path('help/', coreViews.HelpView, name='help'),
]
