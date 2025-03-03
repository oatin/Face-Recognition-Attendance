from django.shortcuts import render, get_object_or_404, redirect
from django.apps import apps
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import json
from django.contrib import messages
from django.contrib.admin.sites import site
from django.forms import modelform_factory

from members.models import Member
from .models import Service, ServiceConfig

from .forms import ServiceConfigForm
from common.decorators import role_required

@role_required(allowed_roles=['admin'])
@login_required
def admin_config(request):
    services = Service.objects.all()

    if request.method == "POST":
        service_id = request.POST.get('service_id')
        key = request.POST.get('key')
        value = request.POST.get('value')

        service = get_object_or_404(Service, id=service_id)

        config, created = ServiceConfig.objects.update_or_create(
            service=service, key=key,
            defaults={'value': value}
        )

        if created:
            messages.success(request, "Config created successfully.")
        else:
            messages.success(request, "Config updated successfully.")

        return redirect('admin_config')

    configs = ServiceConfig.objects.all()

    return render(request, "admin_config.html", {
        'services': services,
        'configs': configs
    })


@role_required(allowed_roles=['admin'])
@login_required
def admin_import_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data_email_id = data.get('data_email_id', [])

            updated_count = 0
            for entry in data_email_id:
                email = entry.get('email')
                student_id = entry.get('student_id')

                try:
                    user = Member.objects.get(email=email)
                    user.student_id = student_id
                    user.save()

                    updated_count += 1
                except Member.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f"User with email {email} not found."})

            return JsonResponse({'success': True, 'message': f'{updated_count} students updated successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error processing the data: {str(e)}"})
    
    return render(request, "admin_import_data.html")

@role_required(allowed_roles=['admin'])
@login_required
def admin_home(request):  
    all_members = Member.objects.all()
    
    context = {
        'all_members': all_members
    }
    
    return render(request, "admin_member.html", context)

MODEL_LIST = {
    "Member": apps.get_model("members", "Member"),
    "Report": apps.get_model("members", "Report"),
    "Notification": apps.get_model("members", "Notification"),
    "Room": apps.get_model("common", "Room"),
    "Courses": apps.get_model("courses", "Course"),
    "Enrollment": apps.get_model("courses", "Enrollment"),
    "Schedule": apps.get_model("attendance", "Schedule"),
    "Attendance": apps.get_model("attendance", "Attendance"),
    "Device": apps.get_model("devices", "Device"),
    "TrainingImage": apps.get_model("devices", "TrainingImage"),
    "FaceModel": apps.get_model("devices", "FaceModel"),
    "FaceScanLog": apps.get_model("devices", "FaceScanLog"),
    "Service": apps.get_model("admin_dashboard", "Service"),
    "ServiceConfig": apps.get_model("admin_dashboard", "ServiceConfig"),
}

@role_required(allowed_roles=['admin'])
@login_required
def admin_dashboard(request):
    model_data = {}
    
    for model_name, ModelClass in MODEL_LIST.items():
        FormClass = modelform_factory(ModelClass, fields="__all__")
        objects = ModelClass.objects.all()
        model_data[model_name] = {
            "objects": objects,
            "form": FormClass(),
        }

    return render(request, "admin_dashboard.html", {"model_data": model_data})

def add_model(request, model_name):
    if model_name not in MODEL_LIST:
        return redirect("admin_dashboard")

    ModelClass = MODEL_LIST[model_name]
    FormClass = modelform_factory(ModelClass, fields="__all__")

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            form.save()
    
    return redirect("admin_dashboard")

def edit_model(request, model_name, pk):
    if model_name not in MODEL_LIST:
        return redirect("admin_dashboard")

    ModelClass = MODEL_LIST[model_name]
    obj = get_object_or_404(ModelClass, pk=pk)
    FormClass = modelform_factory(ModelClass, fields="__all__")

    if request.method == "POST":
        form = FormClass(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")

    return redirect("admin_dashboard")

def delete_model(request, model_name, pk):
    if model_name not in MODEL_LIST:
        return redirect("admin_dashboard")

    ModelClass = MODEL_LIST[model_name]
    obj = get_object_or_404(ModelClass, pk=pk)
    obj.delete()
    
    return redirect("admin_dashboard")