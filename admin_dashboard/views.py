from django.shortcuts import render, get_object_or_404
from django.apps import apps
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from members.models import Member

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