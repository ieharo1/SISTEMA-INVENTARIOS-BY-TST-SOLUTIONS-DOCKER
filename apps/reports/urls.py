from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inventory/pdf/', views.inventory_report_pdf, name='inventory_report_pdf'),
    path('inventory/excel/', views.inventory_report_excel, name='inventory_report_excel'),
    path('movements/pdf/', views.movements_report_pdf, name='movements_report_pdf'),
    path('movements/excel/', views.movements_report_excel, name='movements_report_excel'),
    path('kardex/pdf/<uuid:product_id>/', views.kardex_report_pdf, name='kardex_report_pdf'),
]