from django.urls import path
from . import views

app_name = 'movements'

urlpatterns = [
    path('', views.movement_list, name='movement_list'),
    path('create/<str:movement_type>/', views.movement_create, name='movement_create'),
    path('<uuid:pk>/', views.movement_detail, name='movement_detail'),
    path('kardex/', views.kardex_list, name='kardex'),
    path('kardex/product/<uuid:product_id>/', views.kardex_by_product, name='kardex_by_product'),
]