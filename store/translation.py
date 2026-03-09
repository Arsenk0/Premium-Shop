from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product

# Перекладаємо назву категорії
@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

# Перекладаємо назву та опис товару
@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
