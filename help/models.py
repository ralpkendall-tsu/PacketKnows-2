from django.db import models
from user import models as userModels
from activity import models as activityModels

# Create your models here.
class TestReactivation(models.Model):
    activity = models.ManyToManyField(activityModels.Activity)
    message = models.TextField()
    
    class Meta:
        verbose_name_plural = "Test Reactivations"
    
class StudentIDChange(models.Model):
    student = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE)
    new_school_id = models.BigIntegerField()
    
    class Meta:
        verbose_name_plural = "Student ID Changes"
    
class Notification(models.Model):
    sender = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    receiver = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE, related_name='received_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Notifications"