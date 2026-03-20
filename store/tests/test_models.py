from django.test import TestCase
from store.models import Category, Size

class CategoryModelTest(TestCase):
    def test_category_slug_generation(self):
        category = Category.objects.create(name='Test Category')
        self.assertEqual(category.slug, 'test-category')

class SizeModelTest(TestCase):
    def test_size_str_representation(self):
        size = Size.objects.create(name='XL', type='apparel')
        self.assertEqual(str(size), 'Взуття: XL') # Note: type display might depend on translation
