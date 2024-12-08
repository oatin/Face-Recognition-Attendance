from rest_framework.viewsets import ModelViewSet
from .models import Attendance
from members.serializers import AttendanceSerializer

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer