from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, Value, IntegerField, Q, F

from .models import Course, Enrollment
from attendance.models import Attendance, Schedule
from members.models import Member
from common.models import Room

from datetime import datetime, timedelta, date
from django.core import serializers

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
    else:
        Enrollment.objects.create(student=request.user, course=course)
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
    if request.user.role == "student":
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
    elif request.user.role == "teacher":
        course = get_object_or_404(Course, id=course_id)
    
        today = date.today()
        attendances = Attendance.objects.filter(course=course, date=today)
        schedules = Schedule.objects.filter(course=course) 
        
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('start_time_'):  
                    day_of_week = key.split('_')[2]  
                    start_time = value
                    end_time = request.POST.get(f'end_time_{day_of_week}')
                    try:
                        schedule = schedules.get(day_of_week=day_of_week)
                        schedule.start_time = start_time
                        schedule.end_time = end_time
                        schedule.save()
                    except Schedule.DoesNotExist:
                        pass

        attendances_f = Attendance.objects.select_related('student').values('student__first_name', 'student__last_name', 'date', 'status')
    
        attendances_list = list(attendances_f)
        
        for attendance in attendances_list:
            attendance['date'] = attendance['date'].strftime('%Y-%m-%d')

        context = {
            'course': course,
            'attendances': attendances,
            'schedules':schedules,
            'attendances_data':attendances_list,
        }
        return render(request, 'course_teacher.html', context)

def create_course_view(request):
    if request.method == 'POST':
        if request.user.role == "teacher" or request.user.role == "admin":
            course_code = request.POST.get('course_code')
            course_name = request.POST.get('course_name')
            details = request.POST.get('details')
            image = request.FILES.get('image')
            day_of_week = request.POST.getlist('day_of_week')  
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            room_id = request.POST.get('room')
            
            room = Room.objects.get(id=room_id)
            
            course = Course.objects.create(
                teacher=request.user,
                course_code=course_code, course_name=course_name,
                details=details, image=image
            )
            
            for day in day_of_week:
                Schedule.objects.create(
                    course=course, day_of_week=day,
                    start_time=start_time, end_time=end_time, room=room
                )
            
            return redirect('courses_home')

@login_required
def courses_home(request):
    if request.user.role == "student":
        enrollments = Enrollment.objects.filter(student=request.user)  
        courses = [enrollment.course for enrollment in enrollments] 
        return render(request, 'courses.html', {'courses': courses})
    elif request.user.role == "teacher":
        courses = Course.objects.filter(teacher=request.user)
        rooms = Room.objects.all()
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return render(request, 'courses.html', {'courses': courses,'days_of_week': days_of_week, 'rooms': rooms})
    else:
        return redirect("home")