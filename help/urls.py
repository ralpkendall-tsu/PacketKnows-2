from django.urls import path
from . import views as HelpViews

app_name = 'help'

urlpatterns = [
    path('change-password/', HelpViews.ChangePassword, name="changePassword"),
    path('update-student-number/', HelpViews.UpdateStudentNumber, name="updateStudentNumber"),
    path('test-reactivation/', HelpViews.TestReactivationView, name="testReactivation"),
    path('reactivate-exam/<int:testReactivationID>', HelpViews.ReactivateTestView, name="reactivateExam")
]
