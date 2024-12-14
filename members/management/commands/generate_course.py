import random
from datetime import time, date, timedelta
from django.core.management.base import BaseCommand
from members.models import Member, Student
from courses.models import Course, Enrollment
from attendance.models import Schedule, Attendance, AttendanceStatusEnum

class Command(BaseCommand):
    help = "Generate seed data for Courses, Enrollments, Schedules, and Attendance"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Create Members (Teachers and Students)
        members = []
        for i in range(15):
            role = "teacher" if i < 5 else "student"
            if Member.objects.filter(username=f"user_{i}").exists():
                self.stdout.write(f"User user_{i} already exists. Skipping...")
                continue
            member = Member.objects.create(
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                role=role,
                first_name=f"FirstName{i}",
                last_name=f"LastName{i}",
            )
            members.append(member)

        self.stdout.write(f"Created {len(members)} new members.")

        students = []
        for member in members:
            if member.role == "student":
                student, created = Student.objects.get_or_create(
                    member=member,
                    defaults={"student_id": random.randint(1000, 9999)},
                )
                if created:
                    students.append(student)

        self.stdout.write(f"Created {len(students)} students.")


        # Create Courses
        teachers = members[:5]  # First 5 members are teachers
        courses = []
        for i in range(10):
            course = Course.objects.create(
                course_code=f"COURSE_{i}",
                course_name=f"Course {i}",
                teacher=random.choice(teachers),
            )
            courses.append(course)

        self.stdout.write(f"Created {len(courses)} courses.")

        # Create Enrollments
        students = members[5:]  # Remaining members are students
        enrollments = []
        for course in courses:
            enrolled_students = random.sample(students, k=random.randint(3, 5))
            for student in enrolled_students:
                enrollment = Enrollment.objects.create(
                    student=student, course=course
                )
                enrollments.append(enrollment)

        self.stdout.write(f"Created {len(enrollments)} enrollments.")

        # Create Schedules
        schedules = []
        for course in courses:
            for day in ["Monday", "Wednesday", "Friday"]:
                schedule = Schedule.objects.create(
                    course=course,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(10, 30),
                    room=f"Room {random.randint(1, 10)}",
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
