from django.db import models

from members.models import Member
from courses.models import Course
from attendance.models import AttendanceStatusEnum

import os

class DevicesStatusEnum(models.TextChoices):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Device(models.Model):
    device_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    location = models.CharField(max_length=255)
    last_online = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=DevicesStatusEnum.choices, default=DevicesStatusEnum.INACTIVE
    )
    supports_face_scan = models.BooleanField()
    model_version = models.CharField(max_length=50, blank=True, null=True)
    last_model_update = models.DateTimeField(blank=True, null=True)


def training_image_upload_path(instance, filename):
    return os.path.join(f"training_images/member_{instance.member.id}/", filename)

class TrainingImage(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="training_images"
    )
    file_path = models.ImageField(upload_to=training_image_upload_path) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

class FaceScanLog(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="face_scan_logs")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="face_scan_logs")
    scan_time = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=AttendanceStatusEnum.choices
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="face_scan_logs")


class FaceModel(models.Model):
    model_version = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    model_path = models.CharField(max_length=255)


class FaceModelAssignment(models.Model):
    model = models.ForeignKey(FaceModel, on_delete=models.CASCADE, related_name="assignments")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)