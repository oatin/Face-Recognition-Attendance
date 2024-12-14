import os
from django.core.management.base import BaseCommand
from members.models import Student
from devices.models import TrainingImage 
from django.conf import settings

class Command(BaseCommand):
    help = "Seed training images for existing students"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding training images...")

        students = Student.objects.all()

        image_base_path = "training_images"  

        for student in students:
            member = student.member 
            member_folder = os.path.join(image_base_path, f"member_{member.id}")

           
            fake_image_path = os.path.join(member_folder, f"test.jpg")
            
            TrainingImage.objects.create(
                member=member,
                file_path=fake_image_path,  
            )
            self.stdout.write(f"Created training image for student {student.student_id}: {fake_image_path}")

        self.stdout.write("Seeding complete.")
