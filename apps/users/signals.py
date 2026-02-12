from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    """Asignar grupo por defecto a nuevos usuarios"""
    if created and not instance.groups.exists():
        try:
            operador_group = Group.objects.get(name='Operador')
            instance.groups.add(operador_group)
        except Group.DoesNotExist:
            pass