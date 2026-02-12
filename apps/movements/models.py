from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.users.models import Company
from apps.products.models import Product
from apps.warehouses.models import Warehouse
import uuid

User = get_user_model()

class Movement(models.Model):
    """Modelo de movimientos de inventario"""
    
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
        ('TRANSFER', 'Transferencia'),
        ('ADJUST', 'Ajuste'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='movements')
    
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='Tipo')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Estado')
    
    # Producto y cantidades
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Cantidad')
    
    # Bodegas
    warehouse_from = models.ForeignKey(
        Warehouse, 
        on_delete=models.PROTECT, 
        related_name='movements_from',
        null=True,
        blank=True,
        verbose_name='Bodega origen'
    )
    warehouse_to = models.ForeignKey(
        Warehouse, 
        on_delete=models.PROTECT, 
        related_name='movements_to',
        null=True,
        blank=True,
        verbose_name='Bodega destino'
    )
    
    # Precios
    unit_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Costo unitario'
    )
    total_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Costo total'
    )
    
    # Referencia
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    # Usuario
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movements')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha procesado')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movement_type']),
            models.Index(fields=['status']),
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['warehouse_from', 'warehouse_to']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.sku} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        if not self.total_cost and self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

class Kardex(models.Model):
    """Registro Kardex de movimientos"""
    
    MOVEMENT_TYPES = Movement.MOVEMENT_TYPES
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='kardex')
    
    movement = models.OneToOneField(Movement, on_delete=models.CASCADE, related_name='kardex')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='kardex')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='kardex')
    
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='Tipo')
    
    # Cantidades
    input_quantity = models.IntegerField(default=0, verbose_name='Cantidad entrada')
    output_quantity = models.IntegerField(default=0, verbose_name='Cantidad salida')
    balance_quantity = models.IntegerField(verbose_name='Saldo cantidad')
    
    # Valores
    input_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Valor entrada')
    output_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Valor salida')
    balance_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Saldo valor')
    
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Costo unitario')
    
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='kardex')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    
    class Meta:
        verbose_name = 'Kardex'
        verbose_name_plural = 'Kardex'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['warehouse', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.created_at} - {self.product.sku} - {self.movement_type}"