from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import User, Company
from .forms import UserCreationCustomForm, UserChangeCustomForm, CompanyForm
from apps.audit.decorators import audit_method
from apps.audit.models import AuditLog
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    """Vista de login"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f"Usuario {username} inició sesión")
                messages.success(
                    request, f"Bienvenido {user.get_full_name() or user.username}"
                )
                return redirect("dashboard")  # SIN namespace, es global
            else:
                messages.error(request, "Usuario inactivo")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "users/login.html")


@login_required
def logout_view(request):
    """Vista de logout"""
    logger.info(f"Usuario {request.user.username} cerró sesión")
    logout(request)
    messages.info(request, "Sesión cerrada exitosamente")
    return redirect("users:login")


@login_required
def dashboard(request):
    """Dashboard principal"""
    context = {
        "total_products": Product.objects.filter(is_deleted=False).count(),
        "total_warehouses": Warehouse.objects.filter(is_deleted=False).count(),
        "total_suppliers": Supplier.objects.filter(is_deleted=False).count(),
        "low_stock_count": Inventory.objects.filter(
            quantity__lte=F("min_stock"),
            product__is_deleted=False,
            warehouse__is_deleted=False,
        ).count(),
        "recent_movements": Movement.objects.select_related(
            "product", "warehouse", "created_by"
        ).order_by("-created_at")[:10],
        "stock_by_warehouse": Inventory.objects.values("warehouse__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5],
    }
    return render(request, "dashboard.html", context)


@login_required
@permission_required("users.view_user", raise_exception=True)
def user_list(request):
    """Listado de usuarios"""
    query = request.GET.get("q", "")
    users_list = User.objects.filter(is_deleted=False)

    if query:
        users_list = users_list.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    paginator = Paginator(users_list, 10)
    page = request.GET.get("page")
    users = paginator.get_page(page)

    context = {
        "users": users,
        "query": query,
    }
    return render(request, "users/user_list.html", context)


@login_required
@permission_required("users.add_user", raise_exception=True)
@audit_method(action="CREATE")
def user_create(request):
    """Crear usuario"""
    if request.method == "POST":
        form = UserCreationCustomForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                messages.success(
                    request, f"Usuario {user.username} creado exitosamente"
                )
                logger.info(
                    f"Usuario {request.user.username} creó usuario {user.username}"
                )
            return redirect("users:user_list")
    else:
        form = UserCreationCustomForm()

    context = {"form": form}
    return render(request, "users/user_form.html", context)


@login_required
@permission_required("users.change_user", raise_exception=True)
@audit_method(action="UPDATE")
def user_edit(request, pk):
    """Editar usuario"""
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserChangeCustomForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, f"Usuario {user.username} actualizado")
                logger.info(
                    f"Usuario {request.user.username} editó usuario {user.username}"
                )
            return redirect("users:user_list")
    else:
        form = UserChangeCustomForm(instance=user)

    context = {"form": form, "user_obj": user}
    return render(request, "users/user_form.html", context)


@login_required
@permission_required("users.delete_user", raise_exception=True)
@audit_method(action="DELETE")
def user_delete(request, pk):
    """Eliminar usuario (soft delete)"""
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        with transaction.atomic():
            user.delete()
            messages.success(request, f"Usuario {user.username} eliminado")
            logger.info(
                f"Usuario {request.user.username} eliminó usuario {user.username}"
            )
        return redirect("users:user_list")

    context = {"object": user}
    return render(request, "users/user_confirm_delete.html", context)


@login_required
@permission_required("users.view_user", raise_exception=True)
def user_restore(request, pk):
    """Restaurar usuario eliminado"""
    user = get_object_or_404(User, pk=pk, is_deleted=True)

    with transaction.atomic():
        user.restore()
        messages.success(request, f"Usuario {user.username} restaurado")
        logger.info(f"Usuario {request.user.username} restauró usuario {user.username}")

    return redirect("users:user_list")


@login_required
def profile(request):
    """Perfil de usuario"""
    user = request.user

    if request.method == "POST":
        form = UserChangeCustomForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, "Perfil actualizado exitosamente")
                logger.info(f"Usuario {user.username} actualizó su perfil")
            return redirect("users:profile")
    else:
        form = UserChangeCustomForm(instance=user)

    context = {"form": form, "is_profile": True}
    return render(request, "users/profile.html", context)


@login_required
@permission_required("users.view_company", raise_exception=True)
def company_list(request):
    """Listado de compañías"""
    companies = Company.objects.filter(is_deleted=False)
    return render(request, "users/company_list.html", {"companies": companies})


@login_required
@permission_required("users.add_company", raise_exception=True)
def company_create(request):
    """Crear compañía"""
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                company = form.save()
                messages.success(request, f"Compañía {company.name} creada")
                logger.info(
                    f"Usuario {request.user.username} creó compañía {company.name}"
                )
            return redirect("users:company_list")
    else:
        form = CompanyForm()

    return render(request, "users/company_form.html", {"form": form})
