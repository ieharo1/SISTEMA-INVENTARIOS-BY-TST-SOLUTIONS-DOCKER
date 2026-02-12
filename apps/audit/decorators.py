from functools import wraps
from .models import AuditLog

def audit_method(action=None):
    """Decorador para auditar métodos de vista"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                if request.user.is_authenticated:
                    if hasattr(response, 'context_data') and 'object' in response.context_data:
                        instance = response.context_data['object']
                        AuditLog.log_action(
                            user=request.user,
                            action=action,
                            instance=instance,
                            request=request
                        )
            return response
        return _wrapped_view
    return decorator