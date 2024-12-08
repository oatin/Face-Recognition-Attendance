from django.contrib import admin
from .models import Device,TrainingImage,FaceScanLog,FaceModel,FaceModelAssignment

# Register your models here.
admin.site.register(Device)
admin.site.register(TrainingImage)
admin.site.register(FaceScanLog)
admin.site.register(FaceModel)
admin.site.register(FaceModelAssignment)