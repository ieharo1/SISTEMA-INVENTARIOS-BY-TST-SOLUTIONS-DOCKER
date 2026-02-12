from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.db import transaction
from .models import Inventory
from apps.products.models import Product
from apps.warehouses.models import Warehouse

@login_required
@permission_required('inventory.view_inventory', raise_exception=True)
def inventory_list(request):
    """Listado de inventario"""
    product_id = request.GET.get('product', '')
    warehouse_id = request.GET.get('warehouse', '')
    show_low_stock = request.GET.get('low_stock', False)
    
    inventory_list = Inventory.objects.filter(
        company=request.user.company
    ).select_related('product', 'warehouse')
    
    if product_id:
        inventory_list = inventory_list.filter(product_id=product_id)
    
    if warehouse_id:
        inventory_list = inventory_list.filter(warehouse_id=warehouse_id)
    
    if show_low_stock:
        inventory_list = inventory_list.filter(quantity__lte=F('min_stock'))
    
    paginator = Paginator(inventory_list, 20)
    page = request.GET.get('page')
    inventory = paginator.get_page(page)
    
    products = Product.objects.filter(
        company=request.user.company,
        is_deleted=False,
        is_active=True
    )
    
    warehouses = Warehouse.objects.filter(
        company=request.user.company,
        is_deleted=False,
        is_active=True
    )
    
    context = {
        'inventory': inventory,
        'products': products,
        'warehouses': warehouses,
        'selected_product': product_id,
        'selected_warehouse': warehouse_id,
        'show_low_stock': show_low_stock,
    }
    return render(request, 'inventory/inventory_list.html', context)