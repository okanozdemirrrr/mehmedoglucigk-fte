import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mergen_saas.settings")
django.setup()

import traceback
from accounts.models import User
from rest_framework.test import APIClient

user = User.objects.get(email='bayi@mergen.com')
client = APIClient()
client.force_authenticate(user=user)

try:
    response = client.post('/api/orders/orders/', {'notes': 'test', 'items': [{'product': 1, 'quantity': 1}]}, format='json')
    print('Status:', response.status_code)
    print('Content:', response.content)
except Exception as e:
    traceback.print_exc()
