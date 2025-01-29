from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.courses_home, name="courses_home"),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('search/', views.search_view, name='search_courses'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('create-course/', views.create_course_view, name='create_course'),
]