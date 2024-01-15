from django.urls import path
from . import views as simulationViews

app_name = 'simulation'

urlpatterns = [
    path('restart-activity/<int:activityID>/<int:enrollmentID>/', simulationViews.RestartActivityView, name='reduplicateActivity'),
    path('save-activity/<int:activityID>/', simulationViews.SaveActivityView, name='saveActivity'),
    path('scores/<int:activityID>/', simulationViews.ScoresView, name='scores'),
    path('submit-activity/', simulationViews.SubmitActivityView, name='submitActivity'),

]
