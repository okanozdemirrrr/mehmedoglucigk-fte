from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class TenantMiddleware(MiddlewareMixin):
    """Her istekte kullanıcının tenant'ını request'e ekler"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'tenant'):
                request.tenant = request.user.tenant
            else:
                request.tenant = None
        else:
            request.tenant = None
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api/') and request.user.is_authenticated:
            if not request.tenant and not request.user.is_superuser:
                return JsonResponse({
                    'error': 'Tenant bilgisi bulunamadı'
                }, status=403)
        return None
