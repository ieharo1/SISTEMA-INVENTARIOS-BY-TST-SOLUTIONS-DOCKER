from django.urls import path
from . import views

app_name = 'warehouses'

urlpatterns = [
    path('', views.warehouse_list, name='warehouse_list'),
    path('create/', views.warehouse_create, name='warehouse_create'),
    path('<uuid:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('<uuid:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('<uuid:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
]