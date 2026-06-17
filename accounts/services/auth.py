from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


def authenticate_user(email, password, request=None):
    """
    Tek giriş kaynağı: users tablosu.
    Başarılı olursa (user, token) döner; aksi halde (None, None).
    """
    user = authenticate(request=request, email=email, password=password)
    if user is None or not user.is_active:
        return None, None

    if user.role == 'DEALER':
        if not user.dealer_id or not user.dealer.is_active:
            return None, None

    token, _ = Token.objects.get_or_create(user=user)
    return user, token
