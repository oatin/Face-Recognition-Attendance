from django.test import TestCase
from .models import Member, Student, Notification
from courses.models import Course, Enrollment
from attendance.models import Attendance, Schedule 
from devices.models import *

from django.utils import timezone
from datetime import timedelta

class CourseModelTest(TestCase):

    def test_create_course(self):
        teacher = Member.objects.create(
            username="teacher1", email="teacher1@example.com", role="teacher", first_name="John", last_name="Doe"
        )
        course = Course.objects.create(
            course_code="CS101", course_name="Introduction to Computer Science", teacher=teacher
        )

        self.assertEqual(course.course_code, "CS101")
        self.assertEqual(course.course_name, "Introduction to Computer Science")
        self.assertEqual(course.teacher, teacher)


class ScheduleModelTest(TestCase):

    def test_create_schedule(self):
        teacher = Member.objects.create(username="teacher2", email="teacher2@example.com", role="teacher", first_name="Jane", last_name="Smith")
        course = Course.objects.create(course_code="CS102", course_name="Advanced Computer Science", teacher=teacher)
        schedule = Schedule.objects.create(
            course=course,
            day_of_week="Monday",
            start_time="09:00:00",
            end_time="12:00:00",
            room="Room 101"
        )

        self.assertEqual(schedule.course, course)
        self.assertEqual(schedule.day_of_week, "Monday")
        self.assertEqual(schedule.start_time, "09:00:00")
        self.assertEqual(schedule.end_time, "12:00:00")
        self.assertEqual(schedule.room, "Room 101")


class AttendanceModelTest(TestCase):

    def test_create_attendance(self):
        member = Member.objects.create(username="student1", email="student1@example.com", role="student", first_name="Alice", last_name="Johnson")
        teacher = Member.objects.create(username="teacher3", email="teacher3@example.com", role="teacher", first_name="Bob", last_name="Williams")
        course = Course.objects.create(course_code="CS103", course_name="Data Structures", teacher=teacher)
        schedule = Schedule.objects.create(course=course, day_of_week="Tuesday", start_time="10:00:00", end_time="12:00:00", room="Room 102")

        attendance = Attendance.objects.create(
            schedule=schedule,
            student=member,
            course=course,
            date=timezone.now().date(),
            status="Present",
            time=timezone.now().time()
        )

        self.assertEqual(attendance.schedule, schedule)
        self.assertEqual(attendance.student, member)
        self.assertEqual(attendance.course, course)
        self.assertEqual(attendance.status, "Present")


class DeviceModelTest(TestCase):

    def test_create_device(self):
        device = Device.objects.create(
            device_name="FaceScanDevice1",
            ip_address="192.168.0.1",
            mac_address="00:14:22:01:23:45",
            location="Building A",
            last_online=timezone.now(),
            status="ACTIVE",
            supports_face_scan=True,
            model_version="v1.0",
            last_model_update=timezone.now() - timedelta(days=1)
        )

        self.assertEqual(device.device_name, "FaceScanDevice1")
        self.assertEqual(device.ip_address, "192.168.0.1")
        self.assertEqual(device.mac_address, "00:14:22:01:23:45")
        self.assertEqual(device.location, "Building A")
        self.assertEqual(device.status, "ACTIVE")
        self.assertTrue(device.supports_face_scan)


class FaceScanLogModelTest(TestCase):

    def test_create_face_scan_log(self):
        member = Member.objects.create(username="student2", email="student2@example.com", role="student", first_name="Charlie", last_name="Brown")
        teacher = Member.objects.create(username="teacher4", email="teacher4@example.com", role="teacher", first_name="Dana", last_name="Taylor")
        course = Course.objects.create(course_code="CS104", course_name="Algorithms", teacher=teacher)
        device = Device.objects.create(
            device_name="FaceScanDevice2",
            ip_address="192.168.0.2",
            mac_address="00:14:22:01:23:46",
            location="Building B",
            last_online=timezone.now(),
            status="ACTIVE",
            supports_face_scan=True,
            model_version="v1.1",
            last_model_update=timezone.now() - timedelta(days=2)
        )

        face_scan_log = FaceScanLog.objects.create(
            student=member,
            course=course,
            scan_time=timezone.now(),
            status="Present",
            device=device
        )

        self.assertEqual(face_scan_log.student, member)
        self.assertEqual(face_scan_log.course, course)
        self.assertEqual(face_scan_log.status, "Present")
        self.assertEqual(face_scan_log.device, device)


class NotificationModelTest(TestCase):

    def test_create_notification(self):
        member = Member.objects.create(username="student3", email="student3@example.com", role="student", first_name="Eva", last_name="Davis")
        notification = Notification.objects.create(
            member=member,
            title="Class Reminder",
            message="Don't forget about your class at 9:00 AM tomorrow!",
            status="UNREAD"
        )

        self.assertEqual(notification.member, member)
        self.assertEqual(notification.title, "Class Reminder")
        self.assertEqual(notification.message, "Don't forget about your class at 9:00 AM tomorrow!")
        self.assertEqual(notification.status, "UNREAD")


class StudentModelTest(TestCase):

    def test_create_student(self):
        member = Member.objects.create(username="student4", email="student4@example.com", role="student", first_name="Fred", last_name="Miller")
        student = Student.objects.create(
            member=member,
            student_id=12345
        )

        self.assertEqual(student.member, member)
        self.assertEqual(student.student_id, 12345)