from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AuditLog

@login_required
@permission_required('audit.view_auditlog', raise_exception=True)
def audit_list(request):
    query = request.GET.get('q', '')
    action = request.GET.get('action', '')
    
    audit_list = AuditLog.objects.select_related('user').order_by('-created_at')
    
    if query:
        audit_list = audit_list.filter(
            Q(object_repr__icontains=query) |
            Q(username__icontains=query)
        )
    
    if action:
        audit_list = audit_list.filter(action=action)
    
    paginator = Paginator(audit_list, 20)
    page = request.GET.get('page')
    audits = paginator.get_page(page)
    
    actions = AuditLog.ACTION_CHOICES
    
    return render(request, 'audit/audit_list.html', {
        'audits': audits,
        'actions': actions,
        'selected_action': action,
        'query': query
    })

@login_required
@permission_required('audit.view_auditlog', raise_exception=True)
def audit_detail(request, pk):
    audit = get_object_or_404(AuditLog.objects.select_related('user'), pk=pk)
    return render(request, 'audit/audit_detail.html', {'audit': audit})