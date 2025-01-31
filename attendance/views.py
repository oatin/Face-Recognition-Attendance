from django.shortcuts import redirect, HttpResponse
from .models import Attendance
import csv

def download_attendance_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    attendances = Attendance.objects.select_related('student').values('student__first_name', 'student__last_name', 'date', 'status')
    
    if start_date and end_date:
        attendances = attendances.filter(date__range=[start_date, end_date])
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['First Name', 'Last Name', 'Date', 'Status'])
    
    for attendance in attendances:
        writer.writerow([
            attendance['student__first_name'],
            attendance['student__last_name'],
            attendance['date'].strftime('%Y-%m-%d'),
            attendance['status']
        ])
    
    return response

def update_attendance(request, course_id):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('status_'):
                attendance_id = key.split('_')[1]
                try:
                    attendance = Attendance.objects.get(id=attendance_id)
                    attendance.status = value
                    attendance.save()
                except Attendance.DoesNotExist:
                    continue

    return redirect('course_detail', course_id=course_id)