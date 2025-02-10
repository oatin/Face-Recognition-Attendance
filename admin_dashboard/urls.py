from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_home, name="admin_members"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("api/model/<str:app_label>/<str:model_name>/", views.get_model_data, name="get_model_data"),
    path("api/model/<str:app_label>/<str:model_name>/update/<int:obj_id>/", views.update_model_data, name="update_model_data"),
    path("api/model/<str:app_label>/<str:model_name>/delete/<int:obj_id>/", views.delete_model_data, name="delete_model_data"),
    path("api/model/<str:app_label>/<str:model_name>/add/", views.add_model_data, name="add_model_data"),
]