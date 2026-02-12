from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.users.models import Company
import uuid

class Supplier(models.Model):
    """Modelo de proveedores"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    identification = models.CharField(max_length=50, verbose_name='Identificación fiscal', unique=True)
    
    # Contacto
    contact_name = models.CharField(max_length=100, blank=True, verbose_name='Nombre de contacto')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Teléfono debe tener formato: '+999999999'. Hasta 15 dígitos."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email')
    
    # Dirección
    address = models.CharField(max_length=255, verbose_name='Dirección')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    country = models.CharField(max_length=100, default='Chile', verbose_name='País')
    
    # Información adicional
    website = models.URLField(blank=True, verbose_name='Sitio web')
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    # Control
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']
        indexes = [
            models.Index(fields=['identification']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.identification} - {self.name}"
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurar proveedor eliminado"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()