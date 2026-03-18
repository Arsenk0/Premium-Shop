import requests
import json
import logging
from django.conf import settings
from ..models import OrderItem

logger = logging.getLogger(__name__)

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
            logger.error(f"NP Error in search_cities: {e}")
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
            logger.error(f"NP Error in get_warehouses: {e}")
        return []

class OrderService:
    @staticmethod
    def create_order(cart, user, form_data):
        from ..models import Order, Product
        
        # Create the order object
        order = Order(**form_data)
        if user.is_authenticated:
            order.user = user
        order.save()

        # Create order items with current prices and decrement stock
        for item in cart:
            product = item['product']
            # Refresh product from DB to get current price and stock
            product.refresh_from_db()
            
            order_item = OrderItem(
                order=order,
                product=product,
                price=product.price,  # Use current DB price
                quantity=item['quantity'],
                size=item.get('size')
            )
            order_item.full_clean()  # Validates size selection
            order_item.save()
            
            # Decrement stock
            if product.stock >= item['quantity']:
                product.stock -= item['quantity']
                product.save(update_fields=['stock'])
            else:
                # Should have been caught by cart validation, but safeguard here
                logger.error(f"Stock error for {product.name} during order creation")
            
        return order
