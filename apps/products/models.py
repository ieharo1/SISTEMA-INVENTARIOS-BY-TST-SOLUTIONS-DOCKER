from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from apps.users.models import Company
import uuid

class Category(models.Model):
    """Categoría jerárquica de productos"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
        unique_together = ['company', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    @property
    def full_path(self):
        """Obtener ruta completa de la categoría"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

class Product(models.Model):
    """Modelo de productos"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    
    sku = models.CharField(max_length=50, verbose_name='SKU', db_index=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Categoría')
    
    # Precios
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, 
        validators=[MinValueValidator(0)], 
        verbose_name='Precio costo'
    )
    sale_price = models.DecimalField(
        max_digits=12, decimal_places=2, 
        validators=[MinValueValidator(0)], 
        verbose_name='Precio venta'
    )
    
    # Imágenes
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Imagen')
    
    # Control
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
        unique_together = ['company', 'sku']
        indexes = [
            models.Index(fields=['sku', 'company']),
            models.Index(fields=['name', 'company']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - verificar si tiene inventario"""
        if self.inventories.filter(quantity__gt=0).exists():
            raise models.ProtectedError(
                "No se puede eliminar producto con inventario positivo",
                self
            )
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurar producto eliminado"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    @property
    def margin(self):
        """Calcular margen de ganancia"""
        if self.cost_price > 0:
            return ((self.sale_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def total_stock(self):
        """Obtener stock total del producto"""
        return self.inventories.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})