from rest_framework import permissions

class IsTenantUser(permissions.BasePermission):
    """Kullanıcının tenant'a ait olduğunu kontrol eder"""
    
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'tenant'):
            if request.user.tenant:
                request.tenant = request.user.tenant
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request, 'tenant', None):
            return True
        return False

class IsAdminUser(permissions.BasePermission):
    """Sadece admin kullanıcılar erişebilir"""
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.role in ['SUPERADMIN', 'ADMIN', 'STAFF']

class IsDealerUser(permissions.BasePermission):
    """Bayi kullanıcıları için"""
    
    def has_permission(self, request, view):
        return request.user.role == 'DEALER' and request.user.dealer is not None

class IsDealerOwner(permissions.BasePermission):
    """Kullanıcı sadece kendi bayi verilerine erişebilir"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role in ['ADMIN', 'STAFF']:
            return obj.tenant == request.tenant
        
        if request.user.role == 'DEALER':
            if hasattr(obj, 'dealer'):
                return obj.dealer == request.user.dealer
            elif hasattr(obj, 'tenant'):
                return obj.tenant == request.tenant
        
        return False
