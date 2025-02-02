from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment
from members.models import Member

@receiver(post_save, sender=Member)
def link_enrollments_to_member(sender, instance, created, **kwargs):
    if created:  
        email = instance.email

        enrollments = Enrollment.objects.filter(email=email)
        for enrollment in enrollments:
            enrollment.student = instance 
            enrollment.save()