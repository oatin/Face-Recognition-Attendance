from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def home(req):
    if req.user.is_authenticated:
        if req.user.role == "Student":
            return render(req, "student_home.html")
        else:
            return print("test")
    else:
        return redirect("login")