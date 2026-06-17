from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.mixins import TenantQuerysetMixin, TenantCreateMixin
from core.permissions import IsTenantUser, IsAdminUser, IsDealerUser
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(TenantQuerysetMixin, TenantCreateMixin, viewsets.ModelViewSet):
    queryset = Order.objects.select_related('dealer', 'tenant').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsTenantUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'dealer']
    ordering = ['-order_date']
    
    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and self.request.user.is_authenticated:
            tenant = getattr(self.request.user, 'tenant', None)
            self.request.tenant = tenant
            
        order_count = Order.objects.filter(tenant=tenant).count()
        tenant_code = tenant.slug.upper() if tenant and tenant.slug else f"TN{tenant.id}" if tenant else "MRKZ"
        order_number = f"ORD-{tenant_code}-{order_count + 1:06d}"
        
        if self.request.user.role != 'DEALER':
            raise PermissionDenied('Sipariş yalnızca bayi hesapları tarafından oluşturulabilir.')

        if not self.request.user.dealer_id:
            raise ValidationError('Bayi hesabına dealer kaydı bağlı değil. Yöneticinize başvurun.')

        serializer.save(
            tenant=tenant,
            dealer=self.request.user.dealer,
            order_number=order_number,
            status='PENDING',
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsTenantUser, IsAdminUser])
    def approve(self, request, pk=None):
        order = self.get_object()
        try:
            order.approve(request.user)
            return Response({'status': 'Sipariş onaylandı ve hazırlanıyor'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTenantUser, IsAdminUser])
    def ship(self, request, pk=None):
        order = self.get_object()
        try:
            order.ship_order(request.user)
            return Response({'status': 'Sipariş yola çıktı'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsTenantUser, IsDealerUser])
    def confirm_delivery(self, request, pk=None):
        """Bayi: yoldaki kendi siparişini teslim aldı olarak işaretler."""
        order = self.get_object()
        if order.dealer_id != request.user.dealer_id:
            raise PermissionDenied('Bu sipariş size ait değil.')
        try:
            order.complete_delivery(request.user)
            return Response({'status': 'Teslim alındı'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'], permission_classes=[IsTenantUser, IsAdminUser])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['ON_THE_WAY', 'DELIVERED']:
            return Response(
                {'error': 'Sevk edilmiş veya teslim edilmiş sipariş iptal edilemez'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'CANCELLED'
        order.save()
        return Response({'status': 'Sipariş iptal edildi'})
