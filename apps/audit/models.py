from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
import json
import uuid

User = get_user_model()

class AuditLog(models.Model):
    """Registro de auditoría para todas las operaciones"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('RESTORE', 'Restauración'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('EXPORT', 'Exportación'),
        ('IMPORT', 'Importación'),
        ('VIEW', 'Visualización'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Usuario
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    username = models.CharField(max_length=150, blank=True)
    
    # Acción
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Modelo afectado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Datos
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # IP y User Agent
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # URL
    url = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action} - {self.object_repr}"
    
    @classmethod
    def log_action(cls, user, action, instance, request=None, changes=None, old_values=None, new_values=None):
        """Registrar una acción en la auditoría"""
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(instance)
        
        audit = cls(
            user=user,
            username=user.username if user else 'Sistema',
            action=action,
            content_type=content_type,
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes=changes or {},
            old_values=old_values or {},
            new_values=new_values or {},
        )
        
        if request:
            audit.ip_address = cls.get_client_ip(request)
            audit.user_agent = request.META.get('HTTP_USER_AGENT', '')
            audit.url = request.build_absolute_uri()
            audit.method = request.method
        
        audit.save()
        return audit
    
    @staticmethod
    def get_client_ip(request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip