from django.urls import path, include

from . import views

urlpatterns = [
    path('attendance/<int:course_id>/update/', views.update_attendance, name='update_attendance'),
    path('download-attendance-csv/', views.download_attendance_csv, name='download_attendance_csv'),
]