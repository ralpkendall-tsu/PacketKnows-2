from django.urls import path
from . import views as ClassroomViews

app_name = 'classroom'

urlpatterns = [
    path('active-classes/', ClassroomViews.activeClasses, name='activeClasses'),
    path('completed-classes/', ClassroomViews.completedClasses, name='completedClasses'),
    path('all-classes/', ClassroomViews.allClasses, name='allClasses'),
    path('classes/', ClassroomViews.Classes, name='classes'),
    path('classes/<int:id>/', ClassroomViews.ClassroomView, name='classroom'),
    path('classes-overall-feedback/', ClassroomViews.ClassOverAllFeedbackView, name='classOverAllFeedback'),
    path('top-students/', ClassroomViews.TopPerformingStudentsView, name='topStudents'),
    path('instructorClasses/<str:status>/', ClassroomViews.InstructorClassesView, name='instructorClasses'),
    path('create-class/', ClassroomViews.CreateClassView, name='createClass'),
    path('class-dashboard/<int:classID>/', ClassroomViews.ClassDashboardView, name='classDashboard'),
    path('archive-class/<int:classID>/', ClassroomViews.ArchiveClassView, name='archiveClass'),
    path('delete-class/<int:classID>/', ClassroomViews.DeleteClassView, name='deleteClass'),
    path('remove-student/<int:classID>/<int:userID>', ClassroomViews.RemoveStudentView, name='removeStudent'),
    path('get-students/<int:classroomID>/<str:status>/', ClassroomViews.GetStudentsView, name='getStudents'),
]
