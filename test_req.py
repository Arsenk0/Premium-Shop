import urllib.request
try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/uk/')
    print("STATUS:", response.status)
except Exception as e:
    print("ERROR:", e)
