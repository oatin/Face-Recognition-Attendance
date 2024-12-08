from django.contrib import admin
from .models import Member, Student, Notification

# Register your models here.
admin.site.register(Member)
admin.site.register(Notification)
admin.site.register(Student)