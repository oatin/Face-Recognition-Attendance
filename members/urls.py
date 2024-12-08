from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MemberViewSet
from attendance.views import AttendanceViewSet

router = DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r"attendance", AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]