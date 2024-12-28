from django.db import models
import os
from members.models import Member
from courses.models import Course
from common.models import Room
from common.enums import DevicesStatusEnum, AttendanceStatusEnum

class Device(models.Model):
    device_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name="devices")
    location = models.CharField(max_length=255)
    last_online = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=DevicesStatusEnum.choices, default=DevicesStatusEnum.INACTIVE
    )
    supports_face_scan = models.BooleanField()
    model_version = models.CharField(max_length=50, blank=True, null=True)
    last_model_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.device_name} ({self.room})"

def training_image_upload_path(instance, filename):
    return os.path.join(f"training_images/member_{instance.member.id}/", filename)

class TrainingImage(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="training_images")
    file_path = models.ImageField(upload_to=training_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_path}"

class FaceModel(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE , null=False)
    model_version = models.IntegerField(unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    model_path = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Model v{self.model_version}"

class FaceScanLog(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="face_scan_logs")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="face_scan_logs")
    scan_time = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=AttendanceStatusEnum.choices
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="face_scan_logs")
    attendance = models.ForeignKey('attendance.Attendance', on_delete=models.SET_NULL, null=True, related_name="scan_logs")

    class Meta:
        indexes = [
            models.Index(fields=['scan_time']),
            models.Index(fields=['student', 'course']),
        ]