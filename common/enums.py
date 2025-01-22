from django.db import models

class AttendanceStatusEnum(models.TextChoices):
    PRESENT = "present"
    ABSENT = "absent"
    Leave = "leave"

class SchedulesDayOfWeekEnum(models.TextChoices):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class DevicesStatusEnum(models.TextChoices):
    ACTIVE = "active"
    INACTIVE = "inactive"