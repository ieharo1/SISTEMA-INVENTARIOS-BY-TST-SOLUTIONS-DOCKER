from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum
from django.utils import timezone
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from apps.audit.decorators import audit_method
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('products.view_product', raise_exception=True)
def product_list(request):
    """Listado de productos"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    show_inactive = request.GET.get('show_inactive', False)
    
    products_list = Product.objects.filter(
        company=request.user.company,
        is_deleted=False
    ).select_related('category')
    
    if not show_inactive:
        products_list = products_list.filter(is_active=True)
    
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    paginator = Paginator(products_list, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.filter(
        company=request.user.company,
        is_deleted=False
    )
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'products/product_list.html', context)

@login_required
@permission_required('products.view_product', raise_exception=True)
def product_detail(request, pk):
    """Detalle de producto"""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    # Obtener inventario por bodega
    inventories = product.inventories.select_related('warehouse').all()
    
    # Obtener movimientos recientes
    recent_movements = product.movements.select_related(
        'warehouse', 'created_by'
    ).order_by('-created_at')[:10]
    
    context = {
        'product': product,
        'inventories': inventories,
        'recent_movements': recent_movements,
        'total_stock': product.total_stock,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
@permission_required('products.add_product', raise_exception=True)
@audit_method(action='CREATE')
def product_create(request):
    """Crear producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.company = request.user.company
                product.save()
                messages.success(request, f'Producto {product.name} creado exitosamente')
                logger.info(f'Usuario {request.user.username} creó producto {product.sku}')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {'form': form, 'title': 'Crear Producto'}
    return render(request, 'products/product_form.html', context)

@login_required
@permission_required('products.change_product', raise_exception=True)
@audit_method(action='UPDATE')
def product_edit(request, pk):
    """Editar producto"""
    product = get_object_or_404(
        Product,
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, f'Producto {product.name} actualizado')
                logger.info(f'Usuario {request.user.username} editó producto {product.sku}')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product, 'title': 'Editar Producto'}
    return render(request, 'products/product_form.html', context)

@login_required
@permission_required('products.delete_product', raise_exception=True)
@audit_method(action='DELETE')
def product_delete(request, pk):
    """Eliminar producto (soft delete)"""
    product = get_object_or_404(
        Product,
        pk=pk,
        company=request.user.company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                product.delete()
                messages.success(request, f'Producto {product.name} eliminado')
                logger.info(f'Usuario {request.user.username} eliminó producto {product.sku}')
            return redirect('products:product_list')
        except models.ProtectedError:
            messages.error(request, 'No se puede eliminar el producto porque tiene inventario asociado')
            return redirect('products:product_detail', pk=product.pk)
    
    context = {'object': product}
    return render(request, 'products/product_confirm_delete.html', context)

@login_required
@permission_required('products.view_category', raise_exception=True)
def category_list(request):
    """Listado de categorías"""
    categories = Category.objects.filter(
        company=request.user.company,
        is_deleted=False
    ).prefetch_related('children')
    
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
@permission_required('products.add_category', raise_exception=True)
def category_create(request):
    """Crear categoría"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                category = form.save(commit=False)
                category.company = request.user.company
                category.save()
                messages.success(request, f'Categoría {category.name} creada')
                logger.info(f'Usuario {request.user.username} creó categoría {category.name}')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
        form.fields['parent'].queryset = Category.objects.filter(
            company=request.user.company,
            is_deleted=False
        )
    
    return render(request, 'products/category_form.html', {'form': form})