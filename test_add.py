import urllib.request
import urllib.parse
import json

req = urllib.request.Request('http://127.0.0.1:8000/uk/cart/add/15/', headers={
    'X-Requested-With': 'XMLHttpRequest'
})
try:
    with urllib.request.urlopen(req) as f:
        print("STATUS:", f.status)
        print("BODY:", f.read().decode('utf-8'))
except Exception as e:
    print("ERROR:", e)
