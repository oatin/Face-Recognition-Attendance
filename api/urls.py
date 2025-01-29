from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

from .views import *

router = DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r"attendance", AttendanceViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"device", DeviceViewSet)

router.register(r"Schedule", ScheduleViewSet)
router.register(r"Enrollment", EnrollmentViewSet)
router.register(r"FaceModel", FaceModelViewSet)
router.register(r"TrainingImageViewSet", TrainingImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]