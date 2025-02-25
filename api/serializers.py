from rest_framework import serializers
from members.models import Member
from attendance.models import Attendance, Schedule
from courses.models import Course, Enrollment
from devices.models import Device, FaceModel, TrainingImage
from admin_dashboard.models import ServiceConfig, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ServiceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceConfig
        fields = '__all__'

class TrainingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingImage
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class FaceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceModel
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'