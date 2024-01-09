from django.urls import path
from . import views as ClassroomViews

app_name = 'classroom'

urlpatterns = [
    path('active-classes/', ClassroomViews.activeClasses, name='activeClasses'),
    path('completed-classes/', ClassroomViews.completedClasses, name='completedClasses'),
    path('classes/', ClassroomViews.Classes, name='classes'),
    path('classes/<int:id>', ClassroomViews.ClassroomView, name='classroom')
]
