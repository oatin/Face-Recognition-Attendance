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

    def get_queryset(self):
        queryset = super().get_queryset()

        allowed_params = {"course_id"}
        query_params = set(self.request.query_params.keys())

        invalid_params = query_params - allowed_params
        if invalid_params:
            raise print({param: "This parameter is not allowed." for param in invalid_params})

        course_id = self.request.query_params.get('course_id')
        if course_id:
            if not course_id.isdigit():
                raise print({"course_id": "Must be a valid integer."})
            
            member_course = Enrollment.objects.filter(course_id=course_id).values_list('student_id', flat=True)
            queryset = queryset.filter(member_id__in=member_course)

        return queryset

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all().order_by('day_of_week')
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        allowed_params = {"course"}
        query_params = set(self.request.query_params.keys())

        invalid_params = query_params - allowed_params
        if invalid_params:
            raise print({param: "This parameter is not allowed." for param in invalid_params})

        course_id = self.request.query_params.get('course')
        if course_id:
            if not course_id.isdigit():
                raise print({"course": "Must be a valid integer."})
            queryset = queryset.filter(course=int(course_id))

        return queryset

class EnrollmentViewSet(ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

class FaceModelViewSet(ModelViewSet):
    queryset = FaceModel.objects.all().order_by('updated_at')
    serializer_class = FaceModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        allowed_params = {"course_id"}
        query_params = set(self.request.query_params.keys())

        invalid_params = query_params - allowed_params
        if invalid_params:
            raise print({param: "This parameter is not allowed." for param in invalid_params})

        course_id = self.request.query_params.get('course_id')
        if course_id:
            if not course_id.isdigit():
                raise print({"course_id": "Must be a valid integer."})
            queryset = queryset.filter(course_id=int(course_id))

        return queryset

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
    queryset = Device.objects.all().order_by('id')
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        allowed_params = {"room"}
        query_params = set(self.request.query_params.keys())

        invalid_params = query_params - allowed_params
        if invalid_params:
            raise print({param: "This parameter is not allowed." for param in invalid_params})

        room_id = self.request.query_params.get('room')
        if room_id:
            if not room_id.isdigit():
                raise print({"room": "Must be a valid integer."})
            queryset = queryset.filter(room_id=int(room_id))

        return queryset
