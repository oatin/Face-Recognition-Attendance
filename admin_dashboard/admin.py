from django.contrib import admin
from .models import ServiceConfig, Service
# Register your models here.
admin.site.register(ServiceConfig)
admin.site.register(Service)