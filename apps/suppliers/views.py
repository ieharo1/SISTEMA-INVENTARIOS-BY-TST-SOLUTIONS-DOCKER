from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Supplier
from .forms import SupplierForm
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('suppliers.view_supplier', raise_exception=True)
def supplier_list(request):
    query = request.GET.get('q', '')
    suppliers_list = Supplier.objects.filter(company=request.user.company, is_deleted=False)
    
    if query:
        suppliers_list = suppliers_list.filter(
            Q(name__icontains=query) |
            Q(identification__icontains=query) |
            Q(email__icontains=query)
        )
    
    paginator = Paginator(suppliers_list, 10)
    page = request.GET.get('page')
    suppliers = paginator.get_page(page)
    
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers, 'query': query})

@login_required
@permission_required('suppliers.view_supplier', raise_exception=True)
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company, is_deleted=False)
    return render(request, 'suppliers/supplier_detail.html', {'supplier': supplier})

@login_required
@permission_required('suppliers.add_supplier', raise_exception=True)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                supplier = form.save(commit=False)
                supplier.company = request.user.company
                supplier.save()
                messages.success(request, f'Proveedor {supplier.name} creado exitosamente')
                return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Crear Proveedor'})

@login_required
@permission_required('suppliers.change_supplier', raise_exception=True)
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company, is_deleted=False)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, f'Proveedor {supplier.name} actualizado')
                return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'supplier': supplier, 'title': 'Editar Proveedor'})

@login_required
@permission_required('suppliers.delete_supplier', raise_exception=True)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company, is_deleted=False)
    
    if request.method == 'POST':
        with transaction.atomic():
            supplier.delete()
            messages.success(request, f'Proveedor {supplier.name} eliminado')
        return redirect('suppliers:supplier_list')
    
    return render(request, 'suppliers/supplier_confirm_delete.html', {'object': supplier})