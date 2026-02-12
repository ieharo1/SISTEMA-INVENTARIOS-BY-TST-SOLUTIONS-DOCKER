from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.users.models import Company
from apps.products.models import Product
from apps.warehouses.models import Warehouse
import uuid

class Inventory(models.Model):
    """Modelo de inventario (stock por producto y bodega)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inventories')
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories')
    
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad'
    )
    min_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock mínimo'
    )
    max_stock = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Stock máximo'
    )
    
    location = models.CharField(max_length=100, blank=True, verbose_name='Ubicación en bodega')
    
    last_movement = models.DateTimeField(null=True, blank=True, verbose_name='Último movimiento')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = ['company', 'product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"
    
    @property
    def is_low_stock(self):
        """Verificar si está bajo stock mínimo"""
        return self.quantity <= self.min_stock
    
    @property
    def is_over_stock(self):
        """Verificar si excede stock máximo"""
        return self.max_stock and self.quantity >= self.max_stock