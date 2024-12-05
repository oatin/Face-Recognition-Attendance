from django.db import models
from members.models import Member
from courses.models import Course

class AttendanceStatusEnum(models.TextChoices):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class SchedulesDayOfWeekEnum(models.TextChoices):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(
        max_length=10, choices=SchedulesDayOfWeekEnum.choices
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100)


class Attendance(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="attendances") 
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=AttendanceStatusEnum.choices
    )
    time = models.TimeField()