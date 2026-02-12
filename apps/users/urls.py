from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Usuarios
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<uuid:pk>/edit/', views.user_edit, name='user_edit'),
    path('<uuid:pk>/delete/', views.user_delete, name='user_delete'),
    path('<uuid:pk>/restore/', views.user_restore, name='user_restore'),
    
    # Compañías
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
]