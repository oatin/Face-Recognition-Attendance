import random
from django.core.management.base import BaseCommand
from members.models import Member, Notification, Student
from members.models import MembersRoleEnum, NotificationsStatusEnum

class Command(BaseCommand):
    help = "Generate seed data for Members, Notifications, and Students"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Create Members
        members = []
        for i in range(10):
            member = Member.objects.create(
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                role=random.choice([role[0] for role in MembersRoleEnum.choices]),
                first_name=f"FirstName{i}",
                last_name=f"LastName{i}",
            )
            members.append(member)

        self.stdout.write(f"Created {len(members)} members.")

        # Create Students
        students = []
        for i, member in enumerate(members[:5]):  # First 5 members as students
            student = Student.objects.create(
                member=member,
                student_id=1000 + i,
            )
            students.append(student)

        self.stdout.write(f"Created {len(students)} students.")

        # Create Notifications
        notifications = []
        for member in members:
            for j in range(3):  # Each member gets 3 notifications
                notification = Notification.objects.create(
                    member=member,
                    title=f"Notification {j} for {member.username}",
                    message=f"This is message {j} for {member.username}.",
                    status=random.choice(
                        [status[0] for status in NotificationsStatusEnum.choices]
                    ),
                )
                notifications.append(notification)

        self.stdout.write(f"Created {len(notifications)} notifications.")
        self.stdout.write("Seeding complete.")
