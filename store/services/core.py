import requests
import json
import logging
from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.utils.translation import gettext as _
from ..models import OrderItem

logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    """Raised when there is not enough stock to fulfill an order."""
    pass


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
            response = requests.post(cls.API_URL, json=payload, timeout=10)
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
            response = requests.post(cls.API_URL, json=payload, timeout=10)
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

        with transaction.atomic():
            # Create the order object
            order = Order(**form_data)
            if user.is_authenticated:
                order.user = user
            
            # Apply coupon and discount from cart
            if cart.coupon:
                coupon = cart.coupon
                email = form_data.get('email')
                
                # Check if coupon was already used by this user or email
                usage_filter = Q(coupon=coupon)
                user_filter = Q(user=user) if user.is_authenticated else Q(pk__isnull=True)
                email_filter = Q(email=email)
                
                # We check for any successful/existing orders with this coupon
                if Order.objects.filter(usage_filter & (user_filter | email_filter)).exists():
                    raise ValueError(_("Ви вже використовували цей промокод."))
                
                order.coupon = coupon
                order.discount_amount = cart.get_discount()
            
            order.save()

            # Create order items with current prices and decrement stock
            for item in cart:
                product = item['product']
                # Refresh product from DB to get current price and stock
                product.refresh_from_db()
                quantity = item['quantity']

                order_item = OrderItem(
                    order=order,
                    product=product,
                    price=product.price,  # Use current DB price
                    quantity=quantity,
                    size=item.get('size')
                )
                order_item.full_clean()  # Validates size selection
                order_item.save()

                # Atomically decrement stock using F() to prevent race conditions
                updated = Product.objects.filter(
                    id=product.id,
                    stock__gte=quantity
                ).update(stock=F('stock') - quantity)

                if not updated:
                    raise InsufficientStockError(
                        f"Недостатньо товару '{product.name}' на складі. "
                        f"Доступно: {product.stock}, потрібно: {quantity}"
                    )

        return order
