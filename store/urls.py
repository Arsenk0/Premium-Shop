from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('set-currency/', views.set_currency, name='set_currency'),
    path('set-preferences/', views.set_preferences, name='set_preferences'),
    path('search/', views.product_search, name='product_search'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews_page, name='reviews_page'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Cart
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<str:item_key>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<str:item_key>/', views.cart_update, name='cart_update'),
    path('cart/sidebar-data/', views.cart_sidebar_data, name='cart_sidebar_data'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('coupon/apply/', views.coupon_apply, name='coupon_apply'),
    path('coupon/remove/', views.coupon_remove, name='coupon_remove'),
    
    # Orders
    path('order/create/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.order_list, name='order_list'),
    
    # API
    path('api/nova-poshta/cities/', views.nova_poshta_cities, name='api_np_cities'),
    path('api/nova-poshta/warehouses/', views.nova_poshta_warehouses, name='api_np_warehouses'),
    path('api/search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    
    # ==============================================================
    # ШЛЯХИ, ЯКІ МИ ПІДНЯЛИ ВИЩЕ (Wishlist та Reviews)
    # ==============================================================
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist_list'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),

    # ==============================================================
    # ДИНАМІЧНІ ШЛЯХИ (ЗАВЖДИ ПОВИННІ БУТИ В САМОМУ НИЗУ!)
    # ==============================================================
    path('<str:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('<int:pk>/<str:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]