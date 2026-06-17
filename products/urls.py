from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, DealerPriceViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('dealer-prices', DealerPriceViewSet, basename='dealer-price')

urlpatterns = [
    path('', include(router.urls)),
]
