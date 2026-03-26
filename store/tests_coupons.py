from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from store.models import Coupon, Category, Product, Order
from store.cart import Cart
from decimal import Decimal
import datetime

class CouponTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            article='TST-001',
            price=Decimal('100.00'),
            stock=10,
            available=True
        )
        self.coupon = Coupon.objects.create(
            code='SAVE10',
            valid_from=timezone.now() - datetime.timedelta(days=1),
            valid_to=timezone.now() + datetime.timedelta(days=1),
            discount=10,
            active=True
        )
        self.client = Client()

    def test_coupon_model(self):
        """Test coupon model creation and validation."""
        self.assertEqual(str(self.coupon), 'SAVE10')
        self.assertTrue(self.coupon.active)

    def test_cart_discount(self):
        """Test discount calculation in the Cart class."""
        # Setup session for the request
        session = self.client.session
        item_key = f"{self.product.id}_M"
        session['cart'] = {item_key: {'product_id': self.product.id, 'price': str(self.product.price), 'quantity': 1, 'size': 'M'}}
        session['coupon_id'] = self.coupon.id
        session.save()

        # In a real view, the cart would be initialized from the request
        # We can simulate this by manually setting up the Cart
        class MockRequest:
            def __init__(self, session):
                self.session = session
        
        request = MockRequest(session)
        cart = Cart(request)
        
        self.assertEqual(cart.get_discount(), Decimal('10.00'))
        self.assertEqual(cart.get_total_price_after_discount(), Decimal('90.00'))

    def test_coupon_apply_view(self):
        """Test the coupon apply view."""
        response = self.client.post(reverse('store:coupon_apply'), {'code': 'SAVE10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['coupon_id'], self.coupon.id)

        # Test invalid coupon
        self.client.post(reverse('store:coupon_apply'), {'code': 'INVALID'})
        self.assertIsNone(self.client.session['coupon_id'])

    def test_expired_coupon(self):
        """Test that expired coupons are not applied."""
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            valid_from=timezone.now() - datetime.timedelta(days=2),
            valid_to=timezone.now() - datetime.timedelta(days=1),
            discount=10,
            active=True
        )
        response = self.client.post(reverse('store:coupon_apply'), {'code': 'EXPIRED'})
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_inactive_coupon(self):
        """Test that inactive coupons are not applied."""
        inactive_coupon = Coupon.objects.create(
            code='INACTIVE',
            valid_from=timezone.now() - datetime.timedelta(days=1),
            valid_to=timezone.now() + datetime.timedelta(days=1),
            discount=10,
            active=False
        )
        response = self.client.post(reverse('store:coupon_apply'), {'code': 'INACTIVE'})
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_order_creation_with_coupon(self):
        """Test that an order is created with the correct coupon and discount."""
        from store.services.core import OrderService
        from django.contrib.auth.models import AnonymousUser
        
        # Apply coupon to session
        session = self.client.session
        session['coupon_id'] = self.coupon.id
        session.save()
        
        # Mock request with session and user
        class MockRequest:
            def __init__(self, session):
                self.session = session
                self.user = AnonymousUser()
        
        request = MockRequest(session)
        # Add item to cart
        item_key = f"{self.product.id}_M"
        session['cart'] = {item_key: {'product_id': self.product.id, 'price': str(self.product.price), 'quantity': 1, 'size': 'M'}}
        session.save()
        
        cart = Cart(request)
        
        # Order data
        order_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+380991112233',
            'city': 'Kiev',
            'warehouse': 'Branch 1',
            'contact_method': 'telegram',
            'social_handle': '@johndoe'
        }
        
        order = OrderService.create_order(cart, request.user, order_data)
        
        self.assertEqual(order.coupon, self.coupon)
        self.assertEqual(order.discount_amount, Decimal('10.00'))
        self.assertEqual(order.get_total_cost(), Decimal('90.00'))

    def test_coupon_one_time_use_guest(self):
        """Test that a guest cannot use the same coupon twice with the same email."""
        from store.services.core import OrderService
        from django.contrib.auth.models import AnonymousUser
        
        order_data = {
            'first_name': 'Guest',
            'last_name': 'User',
            'email': 'guest@example.com',
            'phone': '+380990000000',
            'city': 'Lviv',
            'warehouse': 'Branch 2',
            'social_handle': '@guest'
        }
        
        # First order with coupon
        item_key = f"{self.product.id}_M"
        mock_session = {'cart': {item_key: {'product_id': self.product.id, 'price': str(self.product.price), 'quantity': 1, 'size': 'M'}}, 'coupon_id': self.coupon.id}
        
        class MockRequest:
            def __init__(self, session):
                self.session = session
                self.user = AnonymousUser()
        
        cart = Cart(MockRequest(mock_session))
        OrderService.create_order(cart, AnonymousUser(), order_data)
        
        # Second attempt with same email and same coupon
        cart2 = Cart(MockRequest(mock_session))
        with self.assertRaises(ValueError):
            OrderService.create_order(cart2, AnonymousUser(), order_data)

    def test_cart_clear_removes_coupon(self):
        """Test that Cart.clear() removes coupon from session."""
        session = self.client.session
        session['cart'] = {'1': {'product_id': 1, 'price': '100', 'quantity': 1}}
        session['coupon_id'] = self.coupon.id
        session.save()
        
        class MockRequest:
            def __init__(self, session):
                self.session = session
        
        cart = Cart(MockRequest(session))
        cart.clear()
        
        self.assertIsNone(session.get('coupon_id'))
