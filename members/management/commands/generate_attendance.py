import random
from datetime import time, date, timedelta
from django.core.management.base import BaseCommand
from members.models import Member, Student
from courses.models import Course, Enrollment
from attendance.models import Schedule, Attendance, AttendanceStatusEnum
from common.models import Room  # Import Room model

class Command(BaseCommand):
    help = "Generate seed data for Courses, Enrollments, Schedules, and Attendance"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        courses = Course.objects.all()
        rooms = Room.objects.all()
        students = Student.objects.all()
        # Create Schedules
        schedules = []
        for course in courses:
            for day in ["Monday", "Wednesday", "Friday"]:
                room = random.choice(rooms)  # Randomly select a room from the created rooms
                schedule = Schedule.objects.create(
                    course=course,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(10, 30),
                    room=room,  # Assign the selected room
                )
                schedules.append(schedule)

        self.stdout.write(f"Created {len(schedules)} schedules.")

        # Create Attendance Records
        attendances = []
        today = date.today()
        for schedule in schedules:
            for student in students:
                for _ in range(3):  # Generate attendance for 3 days
                    attendance_date = today - timedelta(days=random.randint(0, 10))
                    attendance = Attendance.objects.create(
                        schedule=schedule,
                        student=student,
                        course=schedule.course,
                        date=attendance_date,
                        status=random.choice(
                            [status[0] for status in AttendanceStatusEnum.choices]
                        ),
                        time=time(random.randint(9, 10), random.randint(0, 59)),
                    )
                    attendances.append(attendance)

        self.stdout.write(f"Created {len(attendances)} attendance records.")
        self.stdout.write("Seeding complete.")
