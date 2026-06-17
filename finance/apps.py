from django.apps import AppConfig

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = 'Finans ve Fatura Yönetimi'

    def ready(self):
        import finance.signals  # noqa: F401
