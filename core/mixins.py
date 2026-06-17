from django.core.exceptions import PermissionDenied

class TenantQuerysetMixin:
    """Tüm queryset'leri tenant'a göre filtreler"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_superuser:
            return queryset
        
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and self.request.user.is_authenticated:
            tenant = getattr(self.request.user, 'tenant', None)
            self.request.tenant = tenant
            
        if not tenant:
            raise PermissionDenied('Tenant bilgisi bulunamadı')
        
        if self.request.user.role == 'DEALER':
            if hasattr(queryset.model, 'dealer'):
                return queryset.filter(
                    tenant=self.request.tenant,
                    dealer=self.request.user.dealer
                )
        
        return queryset.filter(tenant=self.request.tenant)

class TenantCreateMixin:
    """Yeni kayıtlara otomatik tenant atar"""
    
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            tenant = getattr(self.request, 'tenant', None)
            if not tenant and self.request.user.is_authenticated:
                tenant = getattr(self.request.user, 'tenant', None)
                self.request.tenant = tenant
                
            if not tenant:
                raise PermissionDenied('Tenant bilgisi bulunamadı')
            
            save_kwargs = {'tenant': tenant}
            
            if self.request.user.role == 'DEALER':
                if hasattr(serializer.Meta.model, 'dealer'):
                    save_kwargs['dealer'] = self.request.user.dealer
            
            serializer.save(**save_kwargs)
