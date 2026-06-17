import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _ensure_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return True

    cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', '') or ''
    if not cred_path:
        logger.warning('FIREBASE_CREDENTIALS_PATH tanımlı değil — push bildirimi atlanıyor.')
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        return True
    except Exception:
        logger.exception('Firebase Admin başlatılamadı')
        return False


def send_push_to_token(token, title, body, data=None):
    """Tek bir FCM token'ına bildirim gönderir."""
    if not token:
        return False

    if not _ensure_firebase():
        return False

    try:
        from firebase_admin import messaging

        payload_data = {k: str(v) for k, v in (data or {}).items()}
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=payload_data,
            token=token,
            android=messaging.AndroidConfig(priority='high'),
        )
        messaging.send(message)
        logger.info('FCM gönderildi: %s', title)
        return True
    except Exception:
        logger.exception('FCM gönderimi başarısız (token=%s...)', token[:12])
        return False


def send_push_to_users(users_qs, title, body, data=None):
    """QuerySet içindeki kullanıcılara bildirim gönderir."""
    sent = 0
    for user in users_qs.exclude(fcm_token='').exclude(fcm_token__isnull=True):
        if send_push_to_token(user.fcm_token, title, body, data):
            sent += 1
    return sent


def notify_tenant_distributors(tenant, title, body, data=None):
    """Tenant'taki admin/dağıtıcı kullanıcılara bildirim."""
    from accounts.models import User

    if not tenant:
        return 0

    users = User.objects.filter(
        tenant=tenant,
        role__in=['SUPERADMIN', 'ADMIN', 'STAFF'],
        is_active=True,
    )
    return send_push_to_users(users, title, body, data)


def notify_dealer(dealer, title, body, data=None):
    """Siparişi veren bayinin kullanıcı hesabına bildirim."""
    if not dealer:
        return False

    try:
        user = dealer.user_account
    except Exception:
        user = None

    if not user or not user.fcm_token:
        return False

    return send_push_to_token(user.fcm_token, title, body, data)
