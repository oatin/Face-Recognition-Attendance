import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Attendance
from courses.models import Course

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'attendance_{self.course_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        attendance_id = data.get('attendance_id')
        status = data.get('status')
        
        if attendance_id and status:
            await self.update_attendance_status(attendance_id, status)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'attendance_update',
                    'attendance_id': attendance_id,
                    'status': status
                }
            )

    async def attendance_update(self, event):
        attendance_id = event['attendance_id']
        status = event['status']
        
        await self.send(text_data=json.dumps({
            'attendance_id': attendance_id,
            'status': status
        }))
        
    async def new_attendance(self, event):
        attendance = event['attendance']
        
        await self.send(text_data=json.dumps({
            'type': 'new_attendance',
            'attendance': attendance
        }))
    
    @database_sync_to_async
    def update_attendance_status(self, attendance_id, status):
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            attendance.status = status
            attendance.save()
            return True
        except Attendance.DoesNotExist:
            return False