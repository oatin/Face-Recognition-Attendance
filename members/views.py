from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os

from .models import Member
from attendance.models import Attendance, Schedule
from courses.models import Course, Enrollment
from devices.models import TrainingImage

from common.utils import detect_face_pose
from .forms import MultipleImageUploadForm

from django.utils.timezone import now
from datetime import timedelta
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
                is_valid, detected_pose = detect_face_pose(temp_path)
                
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
        day_of_week = today.strftime('%A')  

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
            {'attendance_data': attendance_data, 'attendance_summary': attendance_summary, 'class_days': class_days, "schedules": schedules, "today": today,},
        )

    elif request.user.role == "teacher":
        return render(request, "teacher_home.html")

    elif request.user.role == "admin":
        return render(request, "admin_home.html")

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
    
def user_login(request):
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect('home')