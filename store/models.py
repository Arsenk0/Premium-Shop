from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Size(models.Model):
    TYPE_CHOICES = [
        ('shoes', 'Взуття'),
        ('apparel', 'Одяг'),
    ]
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='shoes', verbose_name="Тип")
    
    class Meta:
        verbose_name = 'Розмір'
        verbose_name_plural = 'Розміри'
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    article = models.CharField(max_length=50, unique=True, verbose_name="Article/SKU")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    sizes = models.ManyToManyField(Size, related_name='products', blank=True, verbose_name="Доступні розміри")
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Зображення товарів'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    social_handle = models.CharField(max_length=100, blank=True, verbose_name="Нікнейм")
    city = models.CharField(max_length=100, blank=True, verbose_name="Місто")
    city_ref = models.CharField(max_length=100, blank=True)
    warehouse = models.CharField(max_length=255, blank=True, verbose_name="Відділення")
    warehouse_ref = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Профіль {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Користувач")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    social_handle = models.CharField(max_length=100, blank=True, verbose_name="Ваш нікнейм / Номер")
    contact_method = models.CharField(max_length=20, choices=[
        ('TELEGRAM', 'Telegram'),
        ('INSTAGRAM', 'Instagram'),
        ('PHONE', 'Дзвінок по телефону'),
    ], default='TELEGRAM', verbose_name="Спосіб зв'язку")
    city = models.CharField(max_length=100, verbose_name="Місто")
    city_ref = models.CharField(max_length=100, blank=True, verbose_name="Ref міста")
    warehouse = models.CharField(max_length=255, verbose_name="Відділення")
    warehouse_ref = models.CharField(max_length=100, blank=True, verbose_name="Ref відділення")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    status = models.CharField(max_length=20, choices=[
        ('New', 'Нове'),
        ('Processing', 'В обробці'),
        ('Shipped', 'Відправлено'),
        ('Completed', 'Виконано'),
        ('Canceled', 'Скасовано'),
    ], default='New', verbose_name="Статус")

    class Meta:
        ordering = ('-created',)
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Розмір")

    def __str__(self):
        return str(self.id)
