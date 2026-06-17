import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mergen_saas.settings")
django.setup()

import requests
from accounts.models import User
from rest_framework.authtoken.models import Token
import re

user = User.objects.get(email='bayi@mergen.com')
token = Token.objects.get(user=user)
res = requests.post('http://127.0.0.1:8000/api/orders/orders/', headers={'Authorization': 'Token ' + token.key}, json={'notes': 'test', 'items': [{'product': 1, 'quantity': 1}]})

print('Status:', res.status_code)
if res.status_code == 500:
    tb = re.search(r'(?<=<textarea id="traceback_area" cols="140" rows="25">)(.*?)(?=</textarea>)', res.text, re.DOTALL)
    if tb:
        print(tb.group(1).replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'))
    else:
        print("No traceback found in HTML")
        
        # fallback, just search for Exception Value
        val = re.search(r'<th>Exception Value:</th>\s*<td><pre>(.*?)</pre></td>', res.text, re.DOTALL)
        loc = re.search(r'<th>Exception Location:</th>\s*<td>(.*?)</td>', res.text, re.DOTALL)
        if val: print("Exception Value:", val.group(1))
        if loc: print("Exception Location:", loc.group(1))
