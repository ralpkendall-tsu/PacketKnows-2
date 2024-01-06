import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserCategory(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'User Category'
        verbose_name_plural = 'User Categories'

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    category = models.ForeignKey(UserCategory, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to= 'user/icons/', blank=True, null=True)
    # for students and instructor
    school_id = models.BigIntegerField(unique=True, blank=True, null=True)
    # for selfLearner and instructor
    evidences = models.ImageField(upload_to= 'user/evidences/', blank=True, null=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
