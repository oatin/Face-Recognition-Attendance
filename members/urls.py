from django.urls import path, include
from django.views.generic import TemplateView 

from .views import home

urlpatterns = [
    path('', home, name="login"), 
    path('accounts/', include('allauth.urls')), 
]