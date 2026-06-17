from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import TenantQuerysetMixin
from core.permissions import IsTenantUser, IsAdminUser
from .models import Dealer, User
from .serializers import UserSerializer, DealerSerializer
from .services.auth import authenticate_user


class CustomAuthToken(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'E-posta ve şifre zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, token = authenticate_user(email, password, request=request)
        if user is None:
            return Response(
                {'error': 'Geçersiz e-posta veya şifre'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.select_related('tenant', 'dealer').get(pk=user.pk)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class CurrentUserView(APIView):
    """Oturum açmış kullanıcıyı her zaman users tablosundan döner."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.select_related('tenant', 'dealer').get(pk=request.user.pk)
        return Response(UserSerializer(user).data)


class RegisterFCMTokenView(APIView):
    """Giriş yapmış kullanıcının FCM cihaz token'ını kaydeder."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = (request.data.get('fcm_token') or '').strip()
        if not fcm_token:
            return Response(
                {'error': 'fcm_token zorunludur'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.filter(pk=request.user.pk).update(fcm_token=fcm_token)
        return Response({'status': 'FCM token kaydedildi'})


class DealerViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Dealer.objects.select_related('tenant')
    serializer_class = DealerSerializer
    permission_classes = [IsTenantUser, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']
    http_method_names = ['get', 'patch', 'head', 'options']
