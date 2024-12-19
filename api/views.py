from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from members.models import Member, Student
from attendance.models import Attendance, Schedule
from courses.models import Course, Enrollment
from devices.models import Device, FaceModel, FaceModelAssignment, TrainingImage

from .serializers import *

class TrainingImageViewSet(ModelViewSet):
    queryset = TrainingImage.objects.all().order_by('id')
    serializer_class = TrainingImageSerializer
    permission_classes = [IsAuthenticated]

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

class EnrollmentViewSet(ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

class FaceModelViewSet(ModelViewSet):
    queryset = FaceModel.objects.all()
    serializer_class = FaceModelSerializer
    permission_classes = [IsAuthenticated]

class FaceModelAssignmentViewSet(ModelViewSet):
    queryset = FaceModelAssignment.objects.all()
    serializer_class = FaceModelAssignmentSerializer
    permission_classes = [IsAuthenticated]

class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]