from django.urls import path
from . import views as simulationViews

urlpatterns = [
    path('restart-activity/', simulationViews.RestartActivityView, name='restartActivity'),
    path('save-activity/', simulationViews.SaveActivityView, name='saveActivity'),
    path('scores/', simulationViews.ScoresView, name='scores'),
    path('submit-activity/', simulationViews.SubmitActivityView, name='submitActivity'),

]
