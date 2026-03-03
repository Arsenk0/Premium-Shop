from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Size, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'article', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'article']
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'contact_method', 'social_handle', 'paid', 'status', 'created']
    list_filter = ['paid', 'created', 'updated', 'status', 'contact_method']
    search_fields = ['first_name', 'last_name', 'phone', 'social_handle', 'city', 'warehouse']
    
    fieldsets = (
        ('Дані Клієнта', {
            'fields': ('first_name', 'last_name', 'phone', 'contact_method', 'social_handle')
        }),
        ('Доставка (Нова Пошта)', {
            'fields': ('city', 'city_ref', 'warehouse', 'warehouse_ref')
        }),
        ('Статус Замовлення', {
            'fields': ('status', 'paid')
        }),
        ('Дати', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created', 'updated')
    inlines = [OrderItemInline]
