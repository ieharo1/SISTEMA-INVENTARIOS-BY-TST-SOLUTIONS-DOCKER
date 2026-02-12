from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Movement, Kardex
from .services import MovementService
from apps.products.models import Product
from apps.warehouses.models import Warehouse
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('movements.view_movement', raise_exception=True)
def movement_list(request):
    movements_list = Movement.objects.filter(company=request.user.company).select_related(
        'product', 'warehouse_from', 'warehouse_to', 'created_by'
    ).order_by('-created_at')
    
    paginator = Paginator(movements_list, 20)
    page = request.GET.get('page')
    movements = paginator.get_page(page)
    
    return render(request, 'movements/movement_list.html', {'movements': movements})

@login_required
@permission_required('movements.view_movement', raise_exception=True)
def movement_detail(request, pk):
    movement = get_object_or_404(Movement.objects.select_related(
        'product', 'warehouse_from', 'warehouse_to', 'created_by'
    ), pk=pk, company=request.user.company)
    
    return render(request, 'movements/movement_detail.html', {'movement': movement})

@login_required
@permission_required('movements.add_movement', raise_exception=True)
def movement_create(request, movement_type):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        warehouse_id = request.POST.get('warehouse')
        warehouse_to_id = request.POST.get('warehouse_to')
        quantity = int(request.POST.get('quantity', 0))
        unit_cost = float(request.POST.get('unit_cost', 0))
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        
        try:
            product = Product.objects.get(id=product_id, company=request.user.company)
            
            with transaction.atomic():
                if movement_type == 'IN':
                    warehouse = Warehouse.objects.get(id=warehouse_id, company=request.user.company)
                    MovementService.create_entry(
                        product, warehouse, quantity, unit_cost, 
                        request.user, reference, notes
                    )
                    messages.success(request, 'Entrada registrada exitosamente')
                
                elif movement_type == 'OUT':
                    warehouse = Warehouse.objects.get(id=warehouse_id, company=request.user.company)
                    MovementService.create_output(
                        product, warehouse, quantity, unit_cost, 
                        request.user, reference, notes
                    )
                    messages.success(request, 'Salida registrada exitosamente')
                
                elif movement_type == 'TRANSFER':
                    warehouse_from = Warehouse.objects.get(id=warehouse_id, company=request.user.company)
                    warehouse_to = Warehouse.objects.get(id=warehouse_to_id, company=request.user.company)
                    MovementService.create_transfer(
                        product, warehouse_from, warehouse_to, quantity,
                        request.user, reference, notes
                    )
                    messages.success(request, 'Transferencia registrada exitosamente')
                
                elif movement_type == 'ADJUST':
                    warehouse = Warehouse.objects.get(id=warehouse_id, company=request.user.company)
                    MovementService.create_adjustment(
                        product, warehouse, quantity,
                        request.user, notes
                    )
                    messages.success(request, 'Ajuste registrado exitosamente')
                
                return redirect('movements:movement_list')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    products = Product.objects.filter(company=request.user.company, is_active=True, is_deleted=False)
    warehouses = Warehouse.objects.filter(company=request.user.company, is_active=True, is_deleted=False)
    
    context = {
        'movement_type': movement_type,
        'products': products,
        'warehouses': warehouses,
        'title': f'Crear {dict(Movement.MOVEMENT_TYPES).get(movement_type, movement_type)}'
    }
    
    return render(request, 'movements/movement_form.html', context)

@login_required
@permission_required('movements.view_kardex', raise_exception=True)
def kardex_list(request):
    kardex_list = Kardex.objects.filter(company=request.user.company).select_related(
        'product', 'warehouse', 'created_by'
    ).order_by('-created_at')
    
    paginator = Paginator(kardex_list, 20)
    page = request.GET.get('page')
    kardex = paginator.get_page(page)
    
    return render(request, 'movements/kardex_list.html', {'kardex': kardex})

@login_required
@permission_required('movements.view_kardex', raise_exception=True)
def kardex_by_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user.company)
    kardex_list = Kardex.objects.filter(
        company=request.user.company, product=product
    ).select_related('warehouse', 'created_by').order_by('-created_at')
    
    return render(request, 'movements/kardex_by_product.html', {
        'product': product,
        'kardex': kardex_list
    })