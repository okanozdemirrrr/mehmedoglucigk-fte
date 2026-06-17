from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomAuthToken, CurrentUserView, RegisterFCMTokenView, DealerViewSet

router = DefaultRouter()
router.register('dealers', DealerViewSet, basename='dealer')

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('me/', CurrentUserView.as_view(), name='api_current_user'),
    path('fcm-token/', RegisterFCMTokenView.as_view(), name='api_fcm_token'),
    path('', include(router.urls)),
]
