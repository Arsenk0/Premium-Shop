import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from store.models import Category, Product

def populate():
    # Create Categories
    cats = [
        {'name': 'Кросівки', 'slug': 'sneakers'},
        {'name': 'Худі та Світшоти', 'slug': 'hoodies'},
        {'name': 'Футболки', 'slug': 't-shirts'},
    ]

    for cat_data in cats:
        Category.objects.get_or_create(**cat_data)

    # Get categories
    sneakers = Category.objects.get(slug='sneakers')
    hoodies = Category.objects.get(slug='hoodies')
    tshirts = Category.objects.get(slug='t-shirts')

    # Create Products
    products = [
        {
            'category': sneakers,
            'name': 'Nike Air Jordan 1 Retro Low',
            'article': 'AJ1-LOW-001',
            'description': 'Класичні низькі джордани у червоно-білому кольорі. Преміальна шкіра та комфорт.',
            'price': 150.00,
            'stock': 10,
            'available': True
        },
        {
            'category': sneakers,
            'name': 'Adidas Yeezy Boost 350 V2',
            'article': 'YZY-350-V2',
            'description': 'Інноваційний дизайн від Каньє Веста. Неймовірна амортизація Boost.',
            'price': 220.00,
            'stock': 5,
            'available': True
        },
        {
            'category': hoodies,
            'name': 'Oversize Hoodie Black',
            'article': 'HD-OV-BLK',
            'description': 'Базове чорне худі вільного крою. 100% бавовна.',
            'price': 65.00,
            'stock': 20,
            'available': True
        },
        {
            'category': tshirts,
            'name': 'Streetwear Graphic Tee',
            'article': 'TS-GR-01',
            'description': 'Футболка з авторським принтом у стилі стрітвір. Висока щільність тканини.',
            'price': 35.00,
            'stock': 50,
            'available': True
        },
    ]

    for prod_data in products:
        Product.objects.get_or_create(
            article=prod_data['article'],
            defaults=prod_data
        )

    print("Тестові дані успішно додані!")

if __name__ == '__main__':
    populate()
