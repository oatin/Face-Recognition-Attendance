from django.shortcuts import render, get_object_or_404, redirect
from django.apps import apps
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import json
from django.contrib import messages

from members.models import Member
from .models import Service, ServiceConfig

from .forms import ServiceConfigForm

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

@login_required
def admin_home(request):  
    all_members = Member.objects.all()
    
    context = {
        'all_members': all_members
    }
    
    return render(request, "admin_member.html", context)

@login_required
def admin_dashboard(request):
    selected_models = [
        {"app": "members", "model": "Member"},
        {"app": "devices", "model": "Device"},
        {"app": "courses", "model": "Course"},
        {"app": "attendance", "model": "Schedule"},
        {"app": "common", "model": "Room"},
        {"app": "members", "model": "Report"},
        {"app": "admin_dashboard", "model": "Service"},
        {"app": "admin_dashboard", "model": "ServiceConfig"},
    ]
    
    dashboard_data = []
    
    for item in selected_models:
        try:
            model = apps.get_model(item["app"], item["model"])
            dashboard_data.append({
                "name": item["model"],
                "model": item["model"].lower(),
                "app_label": item["app"],
                "count": model.objects.count()
            })
        except LookupError:
            continue  

    return render(request, "admin_dashboard.html", {"dashboard_data": dashboard_data})


@login_required
def get_model_data(request, app_label, model_name):
    try:
        model = apps.get_model(app_label, model_name.capitalize())
        data = list(model.objects.values())
        
        return JsonResponse({"app": app_label, "model": model_name, "data": data})
    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=400)


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'url'):  
            return obj.url
        return super().default(obj)

@login_required
def update_model_data(request, app_label, model_name, obj_id):
    try:
        model = apps.get_model(app_label, model_name.capitalize())
        obj = get_object_or_404(model, id=obj_id)

        if request.method == "POST":
            for key, value in request.POST.items():
                if key in [field.name for field in model._meta.fields]:  
                    setattr(obj, key, value)

            obj.save()

            updated_data = model_to_dict(obj)
            
            for field in model._meta.fields:
                if isinstance(field, models.ImageField) or isinstance(field, models.FileField):
                    updated_data[field.name] = getattr(obj, field.name).url if getattr(obj, field.name) else None

            return JsonResponse({"success": True, "updated_data": updated_data}, encoder=CustomJSONEncoder)

    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=400)

    return JsonResponse({"success": False}, status=400)


@login_required
def delete_model_data(request, app_label, model_name, obj_id):
    try:
        model = apps.get_model(app_label, model_name.capitalize())
        obj = get_object_or_404(model, id=obj_id)
        obj.delete()
        return JsonResponse({"success": True})
    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=400)


@login_required
def add_model_data(request, app_label, model_name):
    try:
        model = apps.get_model(app_label, model_name.capitalize())

        if request.method == "POST":
            valid_data = {
                key: value for key, value in request.POST.items()
                if key in [field.name for field in model._meta.fields] and key not in ["id", "csrfmiddlewaretoken"]
            }

            new_object = model.objects.create(**valid_data)  
            return JsonResponse({"success": True, "new_data": model_to_dict(new_object)})

    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=400)

    return JsonResponse({"success": False}, status=400)