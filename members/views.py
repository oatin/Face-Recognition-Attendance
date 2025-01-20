from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout 
from django.contrib.auth.decorators import login_required

from devices.models import TrainingImage
from .forms import MultipleImageUploadForm
from django.http import JsonResponse
from common.utils import detect_face_pose
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import os

from .models import Member

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
        return render(request, "student_home.html")
    else:
        return HttpResponse("test")

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