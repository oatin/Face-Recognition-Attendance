from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from members.models import Member
from attendance.models import Attendance

from .serializers import MemberSerializer, AttendanceSerializer

class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]