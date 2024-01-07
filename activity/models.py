from django.db import models

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Courses"
        
    def __str__(self):
        return f"{self.name}"

class ActivityCategory(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Activity Categories"

class BaseActivity(models.Model):
    number = models.DecimalField(max_digits=3, decimal_places=2)
    answer_key = models.TextField(blank=True,null=True)
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    training_task = models.FileField(models.FileField(upload_to='training-tasks/'))
    testing_task = models.FileField(models.FileField(upload_to='training-tasks/'))
    max_physical_points = models.PositiveIntegerField()
    max_basic_config_points = models.PositiveIntegerField()
    max_ip_points = models.PositiveIntegerField()
    max_routing_points = models.PositiveIntegerField()
    max_other_points = models.PositiveIntegerField()
    time_limit = models.PositiveIntegerField()
    
    class Meta:
        verbose_name_plural = "Base Activities"
    
class Activity(models.Model):
    base_activity = models.ForeignKey(BaseActivity, on_delete=models.CASCADE)
    mode = models.CharField(max_length=50)
    physical_points = models.PositiveIntegerField()
    basic_config_points = models.PositiveIntegerField()
    ip_points = models.PositiveIntegerField()
    routing_points = models.PositiveIntegerField()
    other_points = models.PositiveIntegerField()
    time_spent = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default="open")
    
    class Meta:
        verbose_name_plural = "Activities"
    