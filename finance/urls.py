from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, CariAccountViewSet, AnalyticsDashboardView, DealerReceivePaymentView

router = DefaultRouter()
router.register('invoices', InvoiceViewSet, basename='invoice')
router.register('cari', CariAccountViewSet, basename='cari')

urlpatterns = [
    path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('dealers/<int:dealer_id>/receive_payment/', DealerReceivePaymentView.as_view(), name='dealer-receive-payment'),
    path('', include(router.urls)),
]
