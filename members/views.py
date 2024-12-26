from django.shortcuts import render, redirect, HttpResponse

def home(req):
    if req.user.is_authenticated:
        if req.user.role == "student":
            return render(req, "student_home.html")
        else:
            return HttpResponse("test")
    else:
        return redirect("login")