from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import logout 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os

from .models import Member, Report
from attendance.models import Attendance, Schedule
from courses.models import Course, Enrollment
from devices.models import TrainingImage, Device
from common.models import Room
from common.utils import predFacePose
from django.utils.timezone import now
from .forms import ReportForm

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

def custom_404(request, exception):
    return render(request, '404.html', status=404)

@login_required
def report_problem(request):
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, "Your report has been submitted successfully.")

            return JsonResponse({"success": True, "message": "Your report has been submitted successfully!"})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

@login_required
def get_member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    data = {
        "first_name": member.first_name,
        "last_name": member.last_name,
        "email": member.email,
        "student_id": member.student_id,
        "role": member.role,
        "userAvatar": member.profile_path.url,
        "last_login": member.last_login.strftime("%Y-%m-%d %H:%M:%S") if member.last_login else None
    }
    
    return JsonResponse(data)

@require_http_methods(["POST"])
def validate_face_poses(request):
    response = {'valid': True, 'errors': [], 'poses_detected': []}
    temp_files = []
    pose_counts = {
        'Left Profile': 0,
        'Right Profile': 0,
        'Frontal Face': 0
    }
    
    try:
        files = request.FILES.getlist('images')
        
        if len(files) < 3:
            return JsonResponse({
                'valid': False,
                'errors': ['Please upload at least 3 images']
            })
            
        for upload in files:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_path = os.path.join(temp_dir, f'temp_{upload.name}')
            with open(temp_path, 'wb+') as destination:
                for chunk in upload.chunks():
                    destination.write(chunk)
            temp_files.append(temp_path)
            
            try:
                is_valid, detected_pose = predFacePose(temp_path)
                
                if is_valid:
                    pose_counts[detected_pose] += 1
                    response['poses_detected'].append({
                        'filename': upload.name,
                        'pose': detected_pose
                    })
                else:
                    response['errors'].append(f"Failed to detect valid pose in {upload.name}: {detected_pose}")
                    
            except Exception as e:
                response['errors'].append(f"Error processing {upload.name}: {str(e)}")
        
        if pose_counts['Left Profile'] == 0:
            response['errors'].append("Missing Left Profile pose")
        if pose_counts['Right Profile'] == 0:
            response['errors'].append("Missing Right Profile pose")
        if pose_counts['Frontal Face'] == 0:
            response['errors'].append("Missing Frontal Face pose")
            
        response['valid'] = len(response['errors']) == 0
        
    except Exception as e:
        response['valid'] = False
        response['errors'].append(f"System error: {str(e)}")
        
    finally:
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception:
                pass
                
    return JsonResponse(response)

@require_http_methods(["POST"])
def save_training_images(request):
    response = {'success': True, 'errors': []}
    
    try:
        user = request.user

        member = Member.objects.get(username=user)

        files = request.FILES.getlist('images')
        
        for upload in files:
            TrainingImage.objects.create(
                member=member,
                file_path=upload
            )
    except Exception as e:
        response['success'] = False
        response['errors'].append(str(e))
        
    return JsonResponse(response)

@login_required
def home(request):
    if request.user.role == "student":
        member = request.user

        attendance_records = Attendance.objects.filter(student=member).order_by('date')

        today = now().date()
        day_of_week = today.strftime('%A').lower()

        enrollments = Enrollment.objects.filter(student=member)

        schedules = Schedule.objects.filter(
            course__in=[enrollment.course for enrollment in enrollments],
            day_of_week=day_of_week
        )

        schedules_calendar = Schedule.objects.filter(
            course__in=[enrollment.course for enrollment in enrollments]
        )

        class_days = sorted(set([schedule.day_of_week for schedule in schedules_calendar])) 

        cumulative_present = 0
        cumulative_absent = 0
        cumulative_leave = 0

        attendance_data = {
            'dates': [],
            'present': [],
            'absent': [],
            'leave': []
        }

        for record in attendance_records:
            attendance_data['dates'].append(record.date.strftime('%Y-%m-%d'))

            if record.status == 'present':
                cumulative_present += 1
            elif record.status == 'absent':
                cumulative_absent += 1
            elif record.status == 'leave':
                cumulative_leave += 1

            attendance_data['present'].append(cumulative_present)
            attendance_data['absent'].append(cumulative_absent)
            attendance_data['leave'].append(cumulative_leave)

        total_classes = attendance_records.count()
        attendance_summary = {
            'total': total_classes,
            'present': cumulative_present,
            'absence': cumulative_absent,
            'leave': cumulative_leave
        }

        return render(
            request,
            "student_home.html",
            {'attendance_data': attendance_data, 'attendance_summary': attendance_summary, 'class_days': class_days, "schedules": schedules},
        )

    elif request.user.role == "teacher":
        teacher = request.user

        today = now().date()
        day_of_week = today.strftime('%A').lower()

        courses_taught = Course.objects.filter(teacher=teacher)
        schedules = Schedule.objects.filter(
            course__in=courses_taught,
            day_of_week=day_of_week
        )

        schedules_calendar = Schedule.objects.filter(
            course__in=courses_taught
        )

        class_days = sorted(set([schedule.day_of_week for schedule in schedules_calendar]))

        attendance_data = {
            'dates': [],
            'present': [],
            'absent': [],
            'leave': []
        }

        attendance_records = Attendance.objects.filter(course__in=courses_taught).order_by('date')

        cumulative_present = 0
        cumulative_absent = 0
        cumulative_leave = 0

        for record in attendance_records:
            if record.date.strftime('%Y-%m-%d') not in attendance_data['dates']:
                attendance_data['dates'].append(record.date.strftime('%Y-%m-%d'))

            if record.status == 'present':
                cumulative_present += 1
            elif record.status == 'absent':
                cumulative_absent += 1
            elif record.status == 'leave':
                cumulative_leave += 1

            attendance_data['present'].append(cumulative_present)
            attendance_data['absent'].append(cumulative_absent)
            attendance_data['leave'].append(cumulative_leave)

        attendance_summary = {
            'total': 0,
            'present': 0,
            'absence': 0,
            'leave': 0
        }
        for course in courses_taught:
            attendance_records = Attendance.objects.filter(course=course)

            attendance_summary['present'] = attendance_records.filter(status='present').count()
            attendance_summary['absence'] = attendance_records.filter(status='absent').count()
            attendance_summary['leave'] = attendance_records.filter(status='leave').count()

            attendance_summary['total'] = attendance_summary['present'] + attendance_summary['leave'] + attendance_summary['absence']
        
        return render(request, "teacher_home.html",{'attendance_summary':attendance_summary, 'class_days': class_days, "schedules": schedules,'attendance_data':attendance_data})

    elif request.user.role == "admin":
        count_student = Member.objects.filter(role='student').count()
        count_teacher = Member.objects.filter(role='teacher').count()
        count_device = Device.objects.count()
        count_course = Course.objects.count()
        reports = Report.objects.all()

        today = timezone.now()

        start_of_this_month = today.replace(day=1)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

        growth_data = Member.objects.filter(date_joined__gte=start_of_last_month).values('date_joined__month').annotate(user_count=Count('id')).order_by('date_joined__month')

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        labels = [months[i['date_joined__month']-1] for i in growth_data]
        data = [i['user_count'] for i in growth_data]

        device_attendance_data = Attendance.objects.values('device__device_name') \
        .annotate(attendance_count=Count('id')) \
        .order_by('device__device_name')
    
        devices = [item['device__device_name'] for item in device_attendance_data]
        attendance_counts = [item['attendance_count'] for item in device_attendance_data]
        
        context = {
            'count_student': count_student,
            'count_teacher': count_teacher,
            'count_device': count_device,
            'count_course': count_course,
            'labels': labels,
            'data': data,
            'devices': devices,
            'attendance_counts': attendance_counts,
            'reports': reports
        }

        return render(request, "admin_home.html", context)
    else:
        return HttpResponse("Unauthorized access")

@login_required
def profile(request):
    if request.method == "POST":
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            request.user.profile_path = profile_picture
            request.user.save()
            return redirect('profile')  
    return render(request, "profile.html")

@login_required
def teacher_student(request):  
    teacher = request.user
    courses = Course.objects.filter(teacher=teacher)
    attendances = Attendance.objects.filter(course__in=courses).select_related('student', 'course')
    
    months = [(str(m).zfill(2), month) for m, month in enumerate(
        ['January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December'], 1)]
    years = list(range(2020, 2101))
    
    context = {
        'teacher': teacher,
        'courses': courses,
        'attendances': attendances,
        'months': months,
        'years': years,
    }
    
    return render(request, "teacher_student.html", context)
    
def user_login(request):
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect('home')