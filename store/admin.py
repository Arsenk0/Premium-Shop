from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Size, ProductImage, Profile, Review
from modeltranslation.admin import TranslationAdmin

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
    search_fields = ['user__username', 'phone', 'city']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['name', 'article', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'article']
    filter_horizontal = ['sizes']
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'phone', 'status', 'paid', 'created']
    list_filter = ['status', 'paid', 'created', 'contact_method']
    search_fields = ['id', 'first_name', 'last_name', 'phone', 'user__username']
    
    fieldsets = (
        ('Прив\'язка до користувача', {
            'fields': ('user',)
        }),
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

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    search_fields = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
