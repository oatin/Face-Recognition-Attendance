from django.db import models
from members.models import Member

class Course(models.Model):
    course_code = models.CharField(max_length=50, unique=True)
    course_name = models.CharField(max_length=255)
    teacher = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name="courses_teacher")
    details = models.TextField(max_length=500)
    create_at = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/',null=True, blank=True, default="course_images/default.jpg")

    def __str__(self):
        return self.course_name

class Enrollment(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="enrollments", null=True, blank=True, default=None)
    email = models.EmailField(null=True, blank=True)  
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'course'], name='unique_enrollment')
        ]

    def __str__(self):
        return f"{self.email or self.student.email} - {self.course.course_name}"