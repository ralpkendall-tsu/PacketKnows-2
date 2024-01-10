from django.db import models
from user import models as userModels
from activity import models as activityModels
from classroom import models as classroomModels

# Create your models here.
class TestReactivation(models.Model):
    student = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(classroomModels.Classroom, on_delete=models.CASCADE)
    activity = models.ForeignKey(activityModels.Activity, on_delete=models.CASCADE)
    message = models.TextField()
    
    class Meta:
        verbose_name_plural = "Test Reactivations"
        
    def __str__(self):
        return f"{self.activity.base_activity.number}"
    
class StudentIDChange(models.Model):
    student = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE)
    new_school_id = models.BigIntegerField()
    
    class Meta:
        verbose_name_plural = "Student ID Changes"
        
    def __str__(self):
        return f"{self.student.email} - {self.new_school_id}"
    
class Notification(models.Model):
    sender = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    receiver = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE, related_name='received_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notifications"
        
    def __str__(self):
        return f"{self.sender.email}: {self.title}"