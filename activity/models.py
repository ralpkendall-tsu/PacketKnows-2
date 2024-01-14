from django.db import models

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = "Courses"
        
    def __str__(self):
        return f"{self.name}"

class ActivityCategory(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Activity Categories"
        
    def __str__(self):
        return f"{self.name}"

class BaseActivity(models.Model):
    number = models.CharField(max_length=4)
    name = models.CharField(max_length=255)
    projectID = models.CharField(max_length=255, unique=True)
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
        
    def __str__(self):
        return f"{self.course.slug} - {self.number} - {self.name}"
    
class Activity(models.Model):
    base_activity = models.ForeignKey(BaseActivity, on_delete=models.CASCADE)
    projectID = models.CharField(max_length=255, unique=True)
    mode = models.CharField(max_length=50)
    physical_points = models.PositiveIntegerField(default=0)
    basic_config_points = models.PositiveIntegerField(default=0)
    ip_points = models.PositiveIntegerField(default=0)
    routing_points = models.PositiveIntegerField(default=0)
    other_points = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default="open")
    
    class Meta:
        verbose_name_plural = "Activities"
        
    def __str__(self):
        return f"{self.id} - {self.base_activity.course.slug} - {self.base_activity.number} - {self.base_activity.name}"
    