from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Sipariş Yönetimi'

    def ready(self):
        import orders.signals  # noqa: F401
