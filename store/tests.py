from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from .models import Category, Product, Size

class StoreModelsTest(TestCase):
    def test_unicode_slug_generation(self):
        category = Category.objects.create(name="Кросівки")
        self.assertEqual(category.slug, slugify("Кросівки", allow_unicode=True))
        
        product = Product.objects.create(
            category=category,
            name="Бігові кросівки",
            article="TEST-123",
            price=100.00,
            available=True
        )
        self.assertEqual(product.slug, slugify("Бігові кросівки", allow_unicode=True))

class CartLogicTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            article="PROD-1",
            price=50.00,
            available=True
        )

    def test_cart_count_is_correct(self):
        # Add product to cart
        self.client.get(reverse('store:cart_add', args=[self.product.id]))
        
        # Check count via view logic (mocking the request)
        from .cart import Cart
        class MockRequest:
            def __init__(self, session):
                self.session = session
        
        mock_req = MockRequest(self.client.session)
        self.assertEqual(len(Cart(mock_req)), 1)

        # Add another of the same product
        self.client.get(reverse('store:cart_add', args=[self.product.id]))
        mock_req.session = self.client.session
        self.assertEqual(len(Cart(mock_req)), 2)

    def test_cart_add_without_size_fails_if_required(self):
        # Product has sizes (added in setUp via ManyToMany if needed, but let's ensure it has some)
        size = Size.objects.create(name="42", type="shoes")
        self.product.sizes.add(size)
        
        response = self.client.get(reverse('store:cart_add', args=[self.product.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_order_item_clean_validation(self):
        from django.core.exceptions import ValidationError
        from .models import Order, OrderItem
        
        size = Size.objects.create(name="42", type="shoes")
        self.product.sizes.add(size)
        
        order = Order.objects.create(first_name="Test", last_name="User", phone="1234567890")
        item = OrderItem(order=order, product=self.product, price=self.product.price, quantity=1)
        
        with self.assertRaises(ValidationError):
            item.clean()

class ProductCatalogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Electronics")
        self.p1 = Product.objects.create(category=self.category, name="A-Laptop", article="LT-1", price=1000, available=True)
        self.p2 = Product.objects.create(category=self.category, name="B-Phone", article="PH-1", price=500, available=True)
        self.s1 = Size.objects.create(name="L", type="apparel")
        self.p1.sizes.add(self.s1)

    def test_filtering_by_price(self):
        response = self.client.get(reverse('store:product_list'), {'max_price': 600})
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0], self.p2)

    def test_sorting_by_price(self):
        response = self.client.get(reverse('store:product_list'), {'sort': 'price_asc'})
        self.assertEqual(response.context['products'][0], self.p2)
        
        response = self.client.get(reverse('store:product_list'), {'sort': 'price_desc'})
        self.assertEqual(response.context['products'][0], self.p1)

    def test_filtering_by_size(self):
        response = self.client.get(reverse('store:product_list'), {'size': 'L'})
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0], self.p1)

class ReviewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="Test")
        self.product = Product.objects.create(category=self.category, name="Test Product", article="TP-1", price=10, available=True)

    def test_add_review(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('store:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Great product!'
        })
        from .models import Review
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great product!')
