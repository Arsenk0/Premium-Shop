import requests
import json
from django.conf import settings

class NovaPoshtaService:
    API_URL = "https://api.novaposhta.ua/v2.0/json/"
    API_KEY = settings.NOVA_POSHTA_API_KEY

    @classmethod
    def search_cities(cls, query):
        payload = {
            "apiKey": cls.API_KEY,
            "modelName": "Address",
            "calledMethod": "getCities",
            "methodProperties": {
                "FindByString": query,
                "Limit": "10"
            }
        }
        try:
            response = requests.post(cls.API_URL, json=payload)
            data = response.json()
            if data.get('success'):
                return [{
                    'name': city['Description'],
                    'ref': city['Ref']
                } for city in data.get('data', [])]
        except Exception as e:
            print(f"NP Error: {e}")
        return []

    @classmethod
    def get_warehouses(cls, city_ref):
        payload = {
            "apiKey": cls.API_KEY,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityRef": city_ref
            }
        }
        try:
            response = requests.post(cls.API_URL, json=payload)
            data = response.json()
            if data.get('success'):
                return [{
                    'name': wh['Description'],
                    'ref': wh['Ref']
                } for wh in data.get('data', [])]
        except Exception as e:
            print(f"NP Error: {e}")
        return []
