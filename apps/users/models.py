from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
import uuid

class Company(models.Model):
    """Modelo para multiempresa"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nombre', unique=True)
    rut = models.CharField(max_length=20, unique=True, verbose_name='RUT')
    address = models.CharField(max_length=255, verbose_name='Dirección')
    phone = models.CharField(max_length=20, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email')
    logo = models.ImageField(upload_to='companies/', null=True, blank=True, verbose_name='Logo')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Compañía'
        verbose_name_plural = 'Compañías'
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

class User(AbstractUser):
    """Modelo de usuario extendido"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True,
        verbose_name='Compañía'
    )
    
    # Campos adicionales
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Teléfono debe tener formato: '+999999999'. Hasta 15 dígitos."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name='Teléfono')
    
    position = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    
    # Avatar
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Avatar')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha eliminación')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
        
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurar soft delete"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    @property
    def role(self):
        """Obtener el rol principal del usuario"""
        groups = self.groups.all()
        if groups:
            return groups[0].name
        return 'Sin rol'
    
    @role.setter
    def role(self, group_name):
        """Asignar rol al usuario"""
        try:
            group = Group.objects.get(name=group_name)
            self.groups.clear()
            self.groups.add(group)
        except Group.DoesNotExist:
            pass