from django.db import models

class AttendanceStatusEnum(models.TextChoices):
    PRESENT = "present"
    ABSENT = "absent"
    Leave = "leave"

class SchedulesDayOfWeekEnum(models.TextChoices):
    MONDAY = "monday", "Monday"
    TUESDAY = "tuesday", "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY = "thursday", "Thursday"
    FRIDAY = "friday", "Friday"
    SATURDAY = "saturday", "Saturday"
    SUNDAY = "sunday", "Sunday"

class DevicesStatusEnum(models.TextChoices):
    ACTIVE = "active"
    INACTIVE = "inactive"