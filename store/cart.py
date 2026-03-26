from decimal import Decimal
from django.conf import settings
from .models import Product, Coupon

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, size=None):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        item_key = f"{product_id}_{size}" if size else product_id

        if item_key not in self.cart:
            self.cart[item_key] = {
                'product_id': product.id,
                'quantity': 1,
                'price': str(product.price),
                'size': size
            }
        else:
            self.cart[item_key]['quantity'] += 1

        self.save()

    def update(self, item_key, action):
        """
        Update the quantity of a product in the cart.
        """
        if item_key in self.cart:
            if action == 'add':
                self.cart[item_key]['quantity'] += 1
            elif action == 'subtract':
                self.cart[item_key]['quantity'] -= 1
                if self.cart[item_key]['quantity'] <= 0:
                    self.remove(item_key)
            elif action == 'delete':
                self.remove(item_key)
            self.save()

    def remove(self, item_key):
        """
        Remove a product from the cart.
        """
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def clear(self):
        # remove cart from session
        self.session['cart'] = {}
        self.session['coupon_id'] = None
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products 
        from the database in an optimized way.
        """
        product_ids = []
        for item in self.cart.values():
             product_ids.append(item['product_id'])
             
        # Fetch products in a single query
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        # Create a copy so we can yield dictionary references safely
        cart = self.cart.copy()
        for item_key, item in cart.items():
            product_id = item['product_id']
            if product_id in product_map:
                item['product'] = product_map[product_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                item['item_key'] = item_key
                yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total cost of the items in the cart.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
