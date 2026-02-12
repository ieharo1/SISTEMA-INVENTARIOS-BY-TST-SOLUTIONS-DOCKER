from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog
import json

User = get_user_model()

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Guardar valores anteriores antes de actualizar"""
    if not sender._meta.abstract and hasattr(instance, '_audit_enabled'):
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                instance._old_values = {}
                
                for field in instance._meta.fields:
                    field_name = field.name
                    old_value = getattr(old_instance, field_name)
                    new_value = getattr(instance, field_name)
                    
                    if old_value != new_value:
                        instance._old_values[field_name] = {
                            'old': str(old_value) if old_value else None,
                            'new': str(new_value) if new_value else None
                        }
            except sender.DoesNotExist:
                instance._old_values = {}
        else:
            instance._old_values = {}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Registrar creación o actualización en auditoría"""
    if not sender._meta.abstract and hasattr(instance, '_audit_enabled'):
        from django.contrib.auth.models import AnonymousUser
        
        # Obtener usuario del request (si existe)
        user = None
        request = getattr(instance, '_audit_request', None)
        
        if request:
            user = request.user if not isinstance(request.user, AnonymousUser) else None
        
        if not user:
            # Intentar obtener usuario del hilo
            from .middleware import get_current_user
            user = get_current_user()
        
        if created:
            AuditLog.log_action(
                user=user,
                action='CREATE',
                instance=instance,
                request=request,
                new_values={field.name: str(getattr(instance, field.name)) 
                           for field in instance._meta.fields}
            )
        else:
            old_values = getattr(instance, '_old_values', {})
            if old_values:
                AuditLog.log_action(
                    user=user,
                    action='UPDATE',
                    instance=instance,
                    request=request,
                    changes=old_values,
                    old_values={k: v['old'] for k, v in old_values.items()},
                    new_values={k: v['new'] for k, v in old_values.items()}
                )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Registrar eliminación en auditoría"""
    if not sender._meta.abstract and hasattr(instance, '_audit_enabled'):
        from .middleware import get_current_user
        user = get_current_user()
        
        AuditLog.log_action(
            user=user,
            action='DELETE',
            instance=instance,
            new_values={field.name: str(getattr(instance, field.name)) 
                       for field in instance._meta.fields}
        )