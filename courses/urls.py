from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.courses_home, name="courses_home"),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('search/', views.search_view, name='search_courses'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('create-course/', views.create_course_view, name='create_course'),
    path('course/<int:course_id>/add_student/', views.add_student, name='teacher_add_student'),
    path('course/<int:course_id>/import_student/', views.create_enrollments, name='import_enrollments'),
    path('kick_student/<int:enrollment_id>/', views.kick_student, name='kick_student'),
]