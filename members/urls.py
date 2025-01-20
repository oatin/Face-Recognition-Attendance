from django.urls import path, include
from django.views.generic import TemplateView 

from . import views

urlpatterns = [
    path('', views.home, name="home"), 
    path('profile/', views.profile, name="profile"), 
    path('login/', views.user_login, name="login"), 
    path('logout/', views.user_logout, name="logout"),
    path('accounts/', include('allauth.urls')), 
    path('validate-face-poses/', views.validate_face_poses, name='validate_face_poses'),
    path('save-training-images/', views.save_training_images, name='save_training_images'),
]