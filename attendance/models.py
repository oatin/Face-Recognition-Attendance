from django.db import models
from members.models import Member
from courses.models import Course
from common.models import Room
from common.enums import AttendanceStatusEnum, SchedulesDayOfWeekEnum

class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(
        max_length=10, choices=SchedulesDayOfWeekEnum.choices
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="schedules")

    def __str__(self):
        return f"{self.course} - {self.day_of_week} {self.start_time}-{self.end_time}"

class Attendance(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=AttendanceStatusEnum.choices
    )
    time = models.TimeField()
    device = models.ForeignKey('devices.Device', on_delete=models.SET_NULL, null=True, related_name="recorded_attendances")

    class Meta:
        indexes = [
            models.Index(fields=['date', 'schedule']),
            models.Index(fields=['student', 'course']),
        ]