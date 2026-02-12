from django.db import models
from django.utils import timezone
from apps.users.models import Company
import uuid

class Warehouse(models.Model):
    """Modelo de bodegas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='warehouses')
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=50, verbose_name='Código', unique=True)
    location = models.CharField(max_length=255, verbose_name='Ubicación')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Control
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['name']
        unique_together = ['company', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - verificar si tiene inventario"""
        if self.inventories.filter(quantity__gt=0).exists():
            raise models.ProtectedError(
                "No se puede eliminar bodega con inventario positivo",
                self
            )
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurar bodega eliminada"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    @property
    def total_products(self):
        """Cantidad de productos únicos en inventario"""
        return self.inventories.filter(quantity__gt=0).count()
    
    @property
    def total_items(self):
        """Cantidad total de items en inventario"""
        return self.inventories.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0