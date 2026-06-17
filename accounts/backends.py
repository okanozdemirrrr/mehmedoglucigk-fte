from django.contrib.auth.backends import ModelBackend

from accounts.models import User


class EmailAuthBackend(ModelBackend):
    """Giriş yalnızca users tablosundaki e-posta + şifre ile doğrulanır."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        login = email or username
        if not login or not password:
            return None

        try:
            user = User.objects.select_related('tenant', 'dealer').get(email__iexact=login)
        except User.DoesNotExist:
            User().set_password(password)
            return None

        if not user.is_active:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related('tenant', 'dealer').get(pk=user_id)
        except User.DoesNotExist:
            return None
