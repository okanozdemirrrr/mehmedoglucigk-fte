from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from decimal import Decimal, InvalidOperation

from accounts.models import Dealer
from core.mixins import TenantQuerysetMixin
from core.permissions import IsTenantUser, IsAdminUser
from .models import Invoice, CariAccount
from .serializers import InvoiceSerializer, CariAccountSerializer
from .analytics import build_dashboard_payload
from .cari_service import record_payment
class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('dealer', 'order', 'tenant')
    serializer_class = InvoiceSerializer
    permission_classes = [IsTenantUser, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'dealer']
    ordering = ['-invoice_date']
    
    @action(detail=True, methods=['post'])
    def send_to_gib(self, request, pk=None):
        invoice = self.get_object()
        try:
            invoice.send_to_gib()
            return Response({
                'status': 'Fatura GİB\'e gönderildi',
                'gib_uuid': invoice.gib_uuid
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CariAccountViewSet(TenantQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CariAccount.objects.select_related('dealer', 'tenant')
    serializer_class = CariAccountSerializer
    permission_classes = [IsTenantUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dealer', 'transaction_type']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == 'DEALER':
            queryset = queryset.filter(dealer=self.request.user.dealer)
        return queryset
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            tenant = getattr(request.user, 'tenant', None)
            request.tenant = tenant

        dealer_id = request.query_params.get('dealer')

        if request.user.role == 'DEALER':
            dealer_id = request.user.dealer.id

        if not dealer_id:
            return Response({'error': 'Bayi ID gerekli'}, status=status.HTTP_400_BAD_REQUEST)

        if not tenant:
            return Response({'error': 'Tenant bilgisi bulunamadı'}, status=status.HTTP_403_FORBIDDEN)

        balance = CariAccount.objects.filter(
            tenant=tenant,
            dealer_id=dealer_id
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({'dealer_id': dealer_id, 'balance': balance})


def _resolve_tenant(request):
    tenant = getattr(request, 'tenant', None)
    if not tenant and request.user.is_authenticated:
        tenant = getattr(request.user, 'tenant', None)
        request.tenant = tenant
    return tenant


class AnalyticsDashboardView(APIView):
    permission_classes = [IsTenantUser, IsAdminUser]

    def get(self, request):
        date_filter = request.query_params.get('date_filter', 'this_month')
        if date_filter not in ('today', 'this_week', 'this_month'):
            date_filter = 'this_month'
        tenant = _resolve_tenant(request)
        return Response(build_dashboard_payload(tenant, date_filter))


class DealerReceivePaymentView(APIView):
    """Admin: bayiden tahsilat kaydı oluşturur."""
    permission_classes = [IsTenantUser, IsAdminUser]

    def post(self, request, dealer_id):
        tenant = _resolve_tenant(request)
        if not tenant:
            return Response(
                {'error': 'Tenant bilgisi bulunamadı'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            dealer = Dealer.objects.get(pk=dealer_id, tenant=tenant)
        except Dealer.DoesNotExist:
            return Response({'error': 'Bayi bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

        raw_amount = request.data.get('amount')
        if raw_amount is None or raw_amount == '':
            return Response({'error': 'Tutar zorunludur'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(raw_amount))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Geçersiz tutar'}, status=status.HTTP_400_BAD_REQUEST)

        method = (request.data.get('method') or 'Nakit/EFT').strip() or 'Nakit/EFT'

        try:
            entry = record_payment(dealer, tenant, amount, method=method)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        balance = CariAccount.objects.filter(
            tenant=tenant,
            dealer=dealer,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return Response({
            'status': 'Tahsilat başarıyla işlendi',
            'entry_id': entry.id,
            'amount': str(amount),
            'current_balance': str(balance),
            'description': entry.description,
        })
