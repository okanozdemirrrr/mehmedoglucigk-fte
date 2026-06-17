"""Render varsayılan start komutu (gunicorn app:app) için kök modül."""
from mergen_saas.wsgi import application as app

__all__ = ['app']
