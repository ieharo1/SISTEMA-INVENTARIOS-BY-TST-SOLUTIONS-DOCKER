from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Warehouse
from .forms import WarehouseForm
from apps.audit.decorators import audit_method
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('warehouses.view_warehouse', raise_exception=True)
def warehouse_list(request):
    """Listado de bodegas"""
    query = request.GET.get('q', '')
    
    warehouses_list = Warehouse.objects.filter(
        company=request.user.company,
        is_deleted=False
    )
    
    if query:
        warehouses_list = warehouses_list.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(location__icontains=query)
        )
    
    paginator = Paginator(warehouses_list, 10)
    page = request.GET.get('page')
    warehouses = paginator.get_page(page)
    
    context = {
        'warehouses': warehouses,
        'query': query,
    }
    return render(request, 'warehouses/warehouse_list.html', context)

@login_required
@permission_required('warehouses.view_warehouse', raise_exception=True)
def warehouse_detail(request, pk):
    """Detalle de bodega"""
    warehouse = get_object_or_404(
        Warehouse,
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    # Obtener inventario de la bodega
    inventories = warehouse.inventories.select_related('product').filter(
        quantity__gt=0
    ).order_by('-quantity')[:20]
    
    # Obtener movimientos recientes
    recent_movements = warehouse.movements.select_related(
        'product', 'created_by'
    ).order_by('-created_at')[:10]
    
    context = {
        'warehouse': warehouse,
        'inventories': inventories,
        'recent_movements': recent_movements,
        'total_products': warehouse.total_products,
        'total_items': warehouse.total_items,
    }
    return render(request, 'warehouses/warehouse_detail.html', context)

@login_required
@permission_required('warehouses.add_warehouse', raise_exception=True)
@audit_method(action='CREATE')
def warehouse_create(request):
    """Crear bodega"""
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                warehouse = form.save(commit=False)
                warehouse.company = request.user.company
                warehouse.save()
                messages.success(request, f'Bodega {warehouse.name} creada exitosamente')
                logger.info(f'Usuario {request.user.username} creó bodega {warehouse.code}')
            return redirect('warehouses:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm()
    
    context = {'form': form, 'title': 'Crear Bodega'}
    return render(request, 'warehouses/warehouse_form.html', context)

@login_required
@permission_required('warehouses.change_warehouse', raise_exception=True)
@audit_method(action='UPDATE')
def warehouse_edit(request, pk):
    """Editar bodega"""
    warehouse = get_object_or_404(
        Warehouse,
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, f'Bodega {warehouse.name} actualizada')
                logger.info(f'Usuario {request.user.username} editó bodega {warehouse.code}')
            return redirect('warehouses:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    
    context = {'form': form, 'warehouse': warehouse, 'title': 'Editar Bodega'}
    return render(request, 'warehouses/warehouse_form.html', context)

@login_required
@permission_required('warehouses.delete_warehouse', raise_exception=True)
@audit_method(action='DELETE')
def warehouse_delete(request, pk):
    """Eliminar bodega (soft delete)"""
    warehouse = get_object_or_404(
        Warehouse,
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                warehouse.delete()
                messages.success(request, f'Bodega {warehouse.name} eliminada')
                logger.info(f'Usuario {request.user.username} eliminó bodega {warehouse.code}')
            return redirect('warehouses:warehouse_list')
        except models.ProtectedError:
            messages.error(request, 'No se puede eliminar la bodega porque tiene inventario asociado')
            return redirect('warehouses:warehouse_detail', pk=warehouse.pk)
    
    context = {'object': warehouse}
    return render(request, 'warehouses/warehouse_confirm_delete.html', context)