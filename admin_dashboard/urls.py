from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_home, name="admin_members"),
    path("admin-import-data/", views.admin_import_data, name="admin_import_data"),
    path("admin-config/", views.admin_config, name="admin_config"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/add/<str:model_name>/", views.add_model, name="add_model"),
    path("admin-dashboard/edit/<str:model_name>/<int:pk>/", views.edit_model, name="edit_model"),
    path("admin-dashboard/delete/<str:model_name>/<int:pk>/", views.delete_model, name="delete_model"),
]