from django.db import models
from user import models as userModels
from activity import models as activityModels

# Create your models here.

    
class Classroom(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='classroom/class-icons/', blank=True, null=True)
    section = models.CharField(max_length=50)
    school_year = models.CharField(max_length=50)
    instructor = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE, related_name='instructor_classrooms', blank=True, null=True)
    students = models.ManyToManyField(userModels.CustomUser, through='Enrollment', related_name='enrolled_classrooms')
    course = models.ForeignKey(activityModels.Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_updated']
        verbose_name_plural = "Classrooms"
        
    def __str__(self):
        return f"{self.name}"
    
class Enrollment(models.Model):
    student = models.ForeignKey(userModels.CustomUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, )
    status = models.CharField(max_length=50, default="training")
    activities = models.ManyToManyField(activityModels.Activity, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Enrollments"
        
    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.classroom.name}"

    
    