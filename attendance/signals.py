from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Attendance

@receiver(post_save, sender=Attendance)
def attendance_post_save(sender, instance, created, **kwargs):
    if created:  
        channel_layer = get_channel_layer()
        
        attendance_data = {
            'id': instance.id,
            'student_name': f"{instance.student.first_name} {instance.student.last_name}",
            'time': instance.time.strftime('%I:%M %p').lower(),
            'status': instance.status,
        }
        
        async_to_sync(channel_layer.group_send)(
            f'attendance_{instance.course.id}',
            {
                'type': 'new_attendance',
                'attendance': attendance_data
            }
        )