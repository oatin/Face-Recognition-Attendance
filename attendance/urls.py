from django.urls import path, include

from . import views

urlpatterns = [
    path('download-attendance-csv/<int:course_id>/', views.download_attendance_csv, name='download_attendance_csv'),
]