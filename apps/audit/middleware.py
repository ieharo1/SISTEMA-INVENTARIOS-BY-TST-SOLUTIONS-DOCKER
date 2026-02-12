from threading import local
from django.utils.deprecation import MiddlewareMixin

_thread_locals = local()

def get_current_user():
    """Obtener usuario actual del thread local"""
    return getattr(_thread_locals, 'user', None)

class AuditMiddleware(MiddlewareMixin):
    """Middleware para agregar usuario y request a los modelos"""
    
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        
        # Agregar usuario a todos los modelos que se guarden en este request
        def patch_model(instance):
            instance._audit_request = request
            return instance
        
        from django.db.models import Model
        old_init = Model.__init__
        
        def new_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            self._audit_request = request
        
        Model.__init__ = new_init
    
    def process_response(self, request, response):
        return response