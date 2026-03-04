from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from .models import Category, Product, Order, OrderItem
from .forms import OrderCreateForm, UserSignupForm
from .services import NovaPoshtaService


def get_cart(request):
    cart = request.session.get('cart', {})
    return cart


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
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
    return render(request, 'store/product/detail.html', {'product': product})


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
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    size = request.GET.get('size')
    
    # Enforce size selection if product has sizes
    if product.sizes.exists() and not size:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Будь ласка, оберіть розмір!'}, status=400)
        return redirect('store:product_detail', id=product.id, slug=product.slug)

    product_key = f"{product_id}_{size}" if size else str(product_id)

    if product_key not in cart:
        cart[product_key] = {'product_id': product_id, 'quantity': 1, 'price': str(product.price), 'size': size}
    else:
        cart[product_key]['quantity'] += 1

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_count': get_cart_count(request),
            'product_name': product.name
        })

    return redirect('store:cart_detail')


def cart_remove(request, item_key):
    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('store:cart_detail')


def cart_update(request, item_key):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        action = request.POST.get('action')

        if item_key in cart:
            if action == 'add':
                cart[item_key]['quantity'] += 1
            elif action == 'subtract':
                cart[item_key]['quantity'] -= 1
                if cart[item_key]['quantity'] <= 0:
                    del cart[item_key]
            elif action == 'delete':
                del cart[item_key]

        request.session['cart'] = cart
        request.session.modified = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'cart_count': get_cart_count(request)
            })

    return redirect('store:cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for item_key, item in cart.items():
        try:
            p_id = item.get('product_id', int(item_key.split('_')[0]) if '_' in item_key else int(item_key))
            product = Product.objects.get(id=p_id)
            item_total = product.price * item['quantity']
            total_price += item_total
            cart_items.append({
                'item_key': item_key,
                'product': product,
                'quantity': item['quantity'],
                'size': item.get('size'),
                'total_price': item_total
            })
        except (Product.DoesNotExist, ValueError):
            continue
    return render(request, 'store/cart/detail.html', {'cart_items': cart_items, 'total_price': total_price})


def cart_sidebar_data(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for item_key, item in cart.items():
        try:
            p_id = item.get('product_id', int(item_key.split('_')[0]) if '_' in item_key else int(item_key))
            product = Product.objects.get(id=p_id)
            item_total = product.price * item['quantity']
            total_price += item_total
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'quantity': item['quantity'],
                'size': item.get('size'),
                'total_price': str(item_total),
                'image_url': product.image.url if product.image else '/static/img/no-image.png'
            })
        except Product.DoesNotExist:
            continue

    return JsonResponse({
        'cart_items': cart_items,
        'total_price': str(total_price),
        'cart_count': sum(item['quantity'] for item in cart_items)
    })


def get_cart_count(request):
    cart = request.session.get('cart', {})
    total = sum(item.get('quantity', 0) for item in cart.values())
    return total


def order_create(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('store:product_list')
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item_key, item in cart.items():
                try:
                    p_id = item.get('product_id', int(item_key.split('_')[0]) if '_' in item_key else int(item_key))
                    product = Product.objects.get(id=p_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=item.get('quantity', 1) if isinstance(item, dict) else 1,
                        size=item.get('size')
                    )
                except (ValueError, Product.DoesNotExist):
                    continue
            request.session['cart'] = {}
            request.session.modified = True
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


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')