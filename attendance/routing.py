from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/attendance/(?P<course_id>\w+)/$', consumers.AttendanceConsumer.as_asgi()),
]