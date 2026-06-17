from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import TenantQuerysetMixin, TenantCreateMixin
from core.permissions import IsTenantUser, IsAdminUser
from .models import Product, Category, DealerPrice
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    DealerPriceSerializer,
    ProductCatalogSerializer,
)


class ProductViewSet(TenantQuerysetMixin, TenantCreateMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'tenant').prefetch_related(
        'option_groups__items'
    )
    serializer_class = ProductSerializer
    permission_classes = [IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['code', 'name', 'barcode']
    ordering_fields = ['code', 'name', 'base_price']
    ordering = ['code']

    @action(detail=False, methods=['get'], url_path='catalog')
    def catalog(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_active=True)
        dealer = getattr(request.user, 'dealer', None) if request.user.role == 'DEALER' else None
        serializer = ProductCatalogSerializer(
            queryset,
            many=True,
            context={'dealer': dealer, 'request': request},
        )
        return Response(serializer.data)


class CategoryViewSet(TenantQuerysetMixin, TenantCreateMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsTenantUser, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']


class DealerPriceViewSet(viewsets.ModelViewSet):
    queryset = DealerPrice.objects.select_related('product', 'dealer', 'dealer__tenant')
    serializer_class = DealerPriceSerializer
    permission_classes = [IsTenantUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dealer', 'product']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTenantUser(), IsAdminUser()]
        return [IsTenantUser()]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'tenant', None)
        if not tenant:
            return DealerPrice.objects.none()

        qs = self.queryset.filter(dealer__tenant=tenant)
        if self.request.user.role == 'DEALER':
            return qs.filter(dealer=self.request.user.dealer)

        dealer_id = self.request.query_params.get('dealer')
        if dealer_id:
            qs = qs.filter(dealer_id=dealer_id)
        return qs
