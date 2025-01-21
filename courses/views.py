from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, Value, IntegerField

from .models import Course, Enrollment
from attendance.models import Attendance
from members.models import Member

from datetime import datetime

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
    member = request.user.student_profile.member
    attendance_summary = Attendance.objects.filter(
        date__month=datetime.now().month  
    ).aggregate(
        total_attendance=Count('id'),  
        present_count=Count(
            Case(
                When(status='Present', then=1),
                output_field=IntegerField()
            )
        ),
        absence_count=Count(
            Case(
                When(status='Absence', then=1),
                output_field=IntegerField()
            )
        ),
        leave_count=Count(
            Case(
                When(status='Leave', then=1),
                output_field=IntegerField()
            )
        ),
        present_percentage=Count(
            Case(
                When(status='Present', then=1),
                output_field=IntegerField()
            )
        ) * 100 / Count('id')
    )

    attendance_data = {
        'total': attendance_summary['total_attendance'],
        'present': attendance_summary['present_count'],
        'absence': attendance_summary['absence_count'],
        'leave': attendance_summary['leave_count'],
        'present_percentage': f"{attendance_summary['present_percentage']:.1f}%",
        'increased': "+30%", 
    }

    if Enrollment.objects.filter(student=member, course=course).exists():
        return render(request, 'course_detail.html', {'course': course,'attendance_data': attendance_data, 'enroll': True})
    
    return render(request, 'course_detail.html', {'course': course, 'enroll': False})

@login_required
def courses_home(request):
    if request.user.role == "student":
        enrollments = Enrollment.objects.filter(student=request.user)  
        courses = [enrollment.course for enrollment in enrollments] 
        return render(request, 'courses.html', {'courses': courses})
    else:
        return HttpResponse("test")