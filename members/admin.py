from django.contrib import admin
from .models import Member , Notification, Report

# Register your models here.
admin.site.register(Member)
admin.site.register(Report)
admin.site.register(Notification)