from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Category, Product, Order, OrderItem, Size, Review
from .forms import OrderCreateForm, UserSignupForm, ReviewForm
from .services import NovaPoshtaService, OrderService
from .tasks import send_order_confirmation_email
from .cart import Cart
from django.utils.translation import gettext as _

def get_cart_count(request):
    """Fallback helper, though we can also just use len(Cart(request))."""
    cart = Cart(request)
    return len(cart)


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Filtering by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filtering by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    # Filtering by size
    size_filter = request.GET.get('size')
    if size_filter:
        products = products.filter(sizes__name=size_filter)
        
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('-created') # Default sorting

    # Pagination
    paginator = Paginator(products, 12) # 12 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Get dynamic filter options
    all_sizes = Size.objects.filter(products__in=Product.objects.filter(available=True)).distinct()
    price_range = Product.objects.filter(available=True).aggregate(Min('price'), Max('price'))

    return render(request, 'store/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'all_sizes': all_sizes,
        'price_range': price_range,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'size': size_filter,
            'sort': sort
        }
    })


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='store.auth_backends.EmailOrUsernameModelBackend')
            return redirect('store:product_list')
    else:
        form = UserSignupForm()
    return render(request, 'store/accounts/signup.html', {'form': form})


@login_required
def profile(request):
    orders = request.user.orders.all()
    return render(request, 'store/accounts/profile.html', {'orders': orders})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.all()
    form = ReviewForm()
    return render(request, 'store/product/detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('store:product_detail', id=product.id, slug=product.slug)
    return redirect('store:product_detail', id=product.id, slug=product.slug)


def product_search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(article__icontains=query),
            available=True
        )
    return render(request, 'store/product/search.html', {'products': results, 'query': query})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.GET.get('size')
    
    # Enforce size selection if product has sizes
    if product.sizes.exists() and not size:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': _('Будь ласка, оберіть розмір!')}, status=400)
        return redirect('store:product_detail', id=product.id, slug=product.slug)

    cart.add(product, size)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_count': len(cart),
            'product_name': product.name
        })

    return redirect('store:cart_detail')


def cart_remove(request, item_key):
    cart = Cart(request)
    cart.remove(item_key)
    return redirect('store:cart_detail')


def cart_update(request, item_key):
    if request.method == 'POST':
        cart = Cart(request)
        action = request.POST.get('action')
        cart.update(item_key, action)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'cart_count': len(cart)
            })

    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart/detail.html', {'cart_items': cart, 'total_price': cart.get_total_price()})


def cart_sidebar_data(request):
    cart = Cart(request)
    cart_items = []
    
    for item in cart:
        # Since cart iteration fetches products, we can use them directly
        product = item['product']
        cart_items.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'quantity': item['quantity'],
            'size': item.get('size'),
            'total_price': str(item['total_price']),
            'image_url': product.image.url if product.image else '/static/img/no-image.png'
        })

    return JsonResponse({
        'cart_items': cart_items,
        'total_price': str(cart.get_total_price()),
        'cart_count': len(cart)
    })


def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('store:product_list')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = OrderService.create_order(cart, request.user, form.cleaned_data)
            
            # Trigger asynchronous email
            send_order_confirmation_email.delay(order.id)
            
            cart.clear()
            return redirect('store:order_success', order_id=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'store/order/create.html', {'cart': cart, 'form': form})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order/success.html', {'order': order})


def nova_poshta_cities(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'data': []})
    cities = NovaPoshtaService.search_cities(query)
    return JsonResponse({'data': cities})


def nova_poshta_warehouses(request):
    city_ref = request.GET.get('city_ref', '')
    if not city_ref:
        return JsonResponse({'data': []})
    warehouses = NovaPoshtaService.get_warehouses(city_ref)
    return JsonResponse({'data': warehouses})


def reviews_page(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'store/reviews.html', {'reviews': reviews})

def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')