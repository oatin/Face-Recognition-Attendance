from django.urls import path, include
from django.conf.urls import handler404

from . import views
handler404 = views.custom_404

urlpatterns = [
    path('', views.home, name="home"), 
    path('profile/', views.profile, name="profile"), 
    path('student/', views.teacher_student, name="teacher_student"), 
    path('login/', views.user_login, name="login"), 
    path('logout/', views.user_logout, name="logout"),
    path('accounts/', include('allauth.urls')), 
    path('report/', views.report_problem, name="report_problem"),
    path("get-member-detail/<int:member_id>/", views.get_member_detail, name="get_member_detail"),
    path('validate-face-poses/', views.validate_face_poses, name='validate_face_poses'),
    path('save-training-images/', views.save_training_images, name='save_training_images'),
]