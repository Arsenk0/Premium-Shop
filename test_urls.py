import os
import django
from django.urls import reverse
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

c = Client()
print("Reversing 'login':", reverse('login'))
print("Reversing 'store:signup':", reverse('store:signup'))
print("Reversing 'store:product_list':", reverse('store:product_list'))

response = c.post('/uk/accounts/login/', {'username': 'test@test.com', 'password': 'wrongpassword'})
print("Login POST status:", response.status_code)
# We expect 200 (form error) since user doesn't exist

response2 = c.post('/uk/i18n/', {'language': 'en', 'next': '/uk/store/'}, HTTP_REFERER='/uk/')
print("Language set redirect:", response2.url) if response2.status_code in (301, 302) else print("Lang set status:", response2.status_code)

