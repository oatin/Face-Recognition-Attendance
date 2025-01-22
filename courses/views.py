from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, Value, IntegerField, Q, F

from .models import Course, Enrollment
from attendance.models import Attendance, Schedule
from members.models import Member

from datetime import datetime, timedelta, date

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if Enrollment.objects.filter(student=request.user.student_profile.member, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
    else:
        Enrollment.objects.create(student=request.user.student_profile.member, course=course)
        messages.success(request, "You have successfully enrolled in the course!")

    return redirect('course_detail', course_id=course_id)


@login_required
def search_view(request):
    term = request.GET.get('term', '')
    if term:
        courses = Course.objects.filter(course_name__icontains=term).values('id', 'course_name')
        return JsonResponse(list(courses), safe=False)
    return JsonResponse([])

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    member = request.user
    
    schedules = Schedule.objects.filter(course=course).select_related('room')
    
    attendance_data = {
        'total': 0,
        'present': 0,
        'absence': 0,
        'leave': 0,
        'present_percentage': "0.0%",
        'absence_percentage': "0.0%",
    }

    if Enrollment.objects.filter(student=member, course=course).exists():
        total_classes = Attendance.objects.filter(course=course, student=member).count()
        present_count = Attendance.objects.filter(course=course, student=member, status='present').count()
        absence_count = Attendance.objects.filter(course=course, student=member, status='absent').count()
        leave_count = Attendance.objects.filter(course=course, student=member, status='leave').count()

        attendance_data.update({
            'total': total_classes,
            'present': present_count,
            'absence': absence_count,
            'leave': leave_count,
            'present_percentage': f"{(present_count / total_classes) * 100:.1f}%" if total_classes > 0 else "0.0%",
            'absence_percentage': f"{(absence_count / total_classes) * 100:.1f}%" if total_classes > 0 else "0.0%"
        })

        return render(request, 'course_detail.html', {
            'course': course,
            'attendance_data': attendance_data,
            'schedules': schedules,
            'enroll': True
        })

    return render(request, 'course_detail.html', {
        'course': course,
        'attendance_data': attendance_data,
        'schedules': schedules,
        'enroll': False
    })

@login_required
def courses_home(request):
    if request.user.role == "student":
        enrollments = Enrollment.objects.filter(student=request.user)  
        courses = [enrollment.course for enrollment in enrollments] 
        return render(request, 'courses.html', {'courses': courses})
    else:
        return HttpResponse("test")