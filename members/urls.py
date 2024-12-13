from django.urls import path, include # New
from django.views.generic import TemplateView # New

from .views import home

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name="login"), # New
    path('accounts/', include('allauth.urls')), # New
]