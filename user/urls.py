from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as userViews

app_name = 'user'

urlpatterns = [
    path('login/', userViews.CustomLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('signup/', userViews.SignupView, name='signup'),
    path('verify/<str:token>/', userViews.VerifyView, name='verify'),
    path('update-profile/', userViews.UpdateProfileView, name='updateProfile'),   
]
