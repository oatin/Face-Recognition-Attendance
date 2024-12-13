from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def home(req):
    if req.user.is_authenticated:
        return HttpResponse("Login แล้ว")
    else:
        return redirect("login")