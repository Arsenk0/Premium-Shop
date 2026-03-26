from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Size(models.Model):
    TYPE_CHOICES = [
        ('shoes', _('Взуття')),
        ('apparel', _('Одяг')),
    ]
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='shoes', verbose_name=_("Тип"))
    sorting_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортування"))

    class Meta:
        verbose_name = _('Розмір')
        verbose_name_plural = _('Розміри')
        ordering = ['type', 'sorting_order', 'name']

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    article = models.CharField(max_length=50, unique=True, verbose_name=_("Article/SKU"))
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    sizes = models.ManyToManyField(Size, related_name='products', blank=True, verbose_name=_("Доступні розміри"))
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товари')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', args=[self.id, self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('Зображення товару')
        verbose_name_plural = _('Зображення товарів')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон"))
    social_handle = models.CharField(max_length=100, blank=True, verbose_name=_("Нікнейм"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("Місто"))
    city_ref = models.CharField(max_length=100, blank=True)
    warehouse = models.CharField(max_length=255, blank=True, verbose_name=_("Відділення"))
    warehouse_ref = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{_("Профіль")} {self.user.username}'


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Промокод"))
    valid_from = models.DateTimeField(verbose_name=_("Дійсний з"))
    valid_to = models.DateTimeField(verbose_name=_("Дійсний до"))
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_("Знижка (%)"))
    active = models.BooleanField(default=True, verbose_name=_("Активний"))

    class Meta:
        verbose_name = _("Купон")
        verbose_name_plural = _("Купони")

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name=_("Користувач"))
    coupon = models.ForeignKey(Coupon, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name=_("Купон"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Сума знижки"))
    first_name = models.CharField(max_length=50, verbose_name=_("Ім'я"))
    last_name = models.CharField(max_length=50, verbose_name=_("Прізвище"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    social_handle = models.CharField(max_length=100, blank=True, verbose_name=_("Ваш нікнейм / Номер"))
    contact_method = models.CharField(max_length=20, choices=[
        ('TELEGRAM', 'Telegram'),
        ('INSTAGRAM', 'Instagram'),
        ('WHATSAPP', 'WhatsApp'),
    ], default='TELEGRAM', verbose_name=_("Спосіб зв'язку"))
    city = models.CharField(max_length=100, verbose_name=_("Місто"))
    city_ref = models.CharField(max_length=100, blank=True, verbose_name=_("Ref міста"))
    warehouse = models.CharField(max_length=255, verbose_name=_("Відділення"))
    warehouse_ref = models.CharField(max_length=100, blank=True, verbose_name=_("Ref відділення"))
    email = models.EmailField(verbose_name=_("Email"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))
    paid = models.BooleanField(default=False, verbose_name=_("Оплачено"))
    status = models.CharField(max_length=20, choices=[
        ('New', _('Нове')),
        ('Processing', _('В обробці')),
        ('Shipped', _('Відправлено')),
        ('Completed', _('Виконано')),
        ('Canceled', _('Скасовано')),
    ], default='New', verbose_name=_("Статус"))

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Замовлення")
        verbose_name_plural = _("Замовлення")

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        total = sum(item.price * item.quantity for item in self.items.all())
        return total - self.discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Розмір"))

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.product.sizes.exists() and not self.size:
            raise ValidationError({'size': _("Будь ласка, оберіть розмір для товару %(product)s") % {'product': self.product.name}})

    def __str__(self):
        return str(self.id)
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name=_("Рейтинг"))
    comment = models.TextField(verbose_name=_("Коментар"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата"))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _("Відгук")
        verbose_name_plural = _("Відгуки")
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_review_per_product')
        ]

    def __str__(self):
        return f'{_("Відгук від")} {self.user.username} {_("на")} {self.product.name}'

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_wishlist_item')
        ]
        verbose_name = _("Список бажань")
        verbose_name_plural = _("Списки бажань")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
