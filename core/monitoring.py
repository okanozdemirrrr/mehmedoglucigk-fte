"""
Monitoring ve Alerting Utilities
Kritik hataları Sentry'ye raporla
"""
import logging
from functools import wraps
from django.conf import settings

logger = logging.getLogger(__name__)

def monitor_critical_operation(operation_name):
    """
    Kritik operasyonları izle (e-fatura, stok düşümü, ödeme)
    Hata durumunda Sentry'ye bildir
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation_name} başarılı: {func.__name__}")
                return result
            
            except Exception as e:
                logger.error(
                    f"{operation_name} HATASI: {str(e)}",
                    exc_info=True,
                    extra={
                        'operation': operation_name,
                        'function': func.__name__,
                        'args': str(args)[:200],
                    }
                )
                
                # Sentry'ye gönder
                if not settings.DEBUG:
                    import sentry_sdk
                    sentry_sdk.capture_exception(e)
                
                raise
        
        return wrapper
    return decorator

def alert_low_stock(product, threshold=10):
    """Stok kritik seviyeye düştüğünde uyarı"""
    if product.stock_quantity <= threshold:
        logger.warning(
            f"KRİTİK STOK: {product.code} - {product.name}",
            extra={
                'product_id': product.id,
                'stock': float(product.stock_quantity),
                'threshold': threshold,
                'tenant': product.tenant.name
            }
        )
        
        if not settings.DEBUG:
            import sentry_sdk
            sentry_sdk.capture_message(
                f"Düşük Stok Uyarısı: {product.code}",
                level='warning'
            )

def alert_failed_invoice(invoice, error):
    """Fatura gönderimi başarısız olduğunda uyarı"""
    logger.error(
        f"FATURA GÖNDERİM HATASI: {invoice.invoice_number}",
        extra={
            'invoice_id': invoice.id,
            'dealer': invoice.dealer.name,
            'amount': float(invoice.total_amount),
            'error': str(error),
            'tenant': invoice.tenant.name
        }
    )
    
    if not settings.DEBUG:
        import sentry_sdk
        sentry_sdk.capture_message(
            f"E-Fatura Hatası: {invoice.invoice_number} - {str(error)}",
            level='error'
        )
