from django.test import TestCase

from members.models import Member
from courses.models import Course
from .models import Attendance, Schedule 

class TestModelRelationship(TestCase):
    def test_schedule_attendance_relationship(self):
        course = Course.objects.create(course_code="CS101", course_name="Math")
        schedule = Schedule.objects.create(
            course=course,
            day_of_week="Monday",
            start_time="10:00",
            end_time="12:00",
            room="Room 101"
        )
        student = Member.objects.create(username="student1", email="student1@example.com")

        attendance = Attendance.objects.create(
            schedule=schedule,
            student=student,
            course=course,
            date="2024-01-01",
            status="Present",
            time="10:05"
        )

        self.assertEqual(attendance.schedule, schedule)
        self.assertEqual(attendance.course, course)
        self.assertEqual(attendance.student, student)
        self.assertIn(attendance, schedule.attendances.all())