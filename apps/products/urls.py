from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Productos
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<uuid:pk>/', views.product_detail, name='product_detail'),
    path('<uuid:pk>/edit/', views.product_edit, name='product_edit'),
    path('<uuid:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Categorías
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
]