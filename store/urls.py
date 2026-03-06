from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews_page, name='reviews_page'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),

    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<str:item_key>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<str:item_key>/', views.cart_update, name='cart_update'),
    path('cart/sidebar-data/', views.cart_sidebar_data, name='cart_sidebar_data'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('api/nova-poshta/cities/', views.nova_poshta_cities, name='api_np_cities'),
    path('api/nova-poshta/warehouses/', views.nova_poshta_warehouses, name='api_np_warehouses'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
]
