from django.contrib.auth.models import AbstractUser
from django.db import models

class MembersRoleEnum(models.TextChoices):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class NotificationsStatusEnum(models.TextChoices):
    UNREAD = "unread"
    READ = "read"


class Member(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=MembersRoleEnum.choices, default=MembersRoleEnum.STUDENT
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_path = models.ImageField(upload_to="profile_images/", null=True, blank=True, default="profile_images/default.jpg")
    student_id = models.CharField(max_length=15, unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    

class Notification(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=10, choices=NotificationsStatusEnum.choices, default=NotificationsStatusEnum.UNREAD
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(Member, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255) 
    description = models.TextField()  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='reports/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"