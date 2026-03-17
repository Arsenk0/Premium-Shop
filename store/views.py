from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from store.models import Category, Product, Order, OrderItem, Size, Review, Wishlist
from store.forms import OrderCreateForm, UserSignupForm, ReviewForm, UserUpdateForm, ProfileUpdateForm
from store.services import NovaPoshtaService, OrderService
from store.services import dashboard_service
from store.tasks import send_order_confirmation_email, send_welcome_email
from store.cart import Cart
from django.utils.translation import gettext as _, get_language
from django.utils import translation
from django.urls import translate_url
from django.conf import settings
import decimal
from decimal import Decimal

class ProductListView(ListView):
    model = Product
    template_name = 'store/product/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None

        # Filtering
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        size_filter = self.request.GET.get('size')
        
        if min_price or max_price:
            try:
                # Use session currency if available, else language-based default
                selected_currency = self.request.session.get('currency')
                language = get_language()
                
                if selected_currency:
                    # Find currency settings by currency code (e.g., 'USD')
                    currency_settings = next((v for v in settings.CURRENCIES.values() if v['code'] == selected_currency), None)
                else:
                    currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
                
                if not currency_settings:
                    currency_settings = settings.CURRENCIES.get('uk')

                rate = Decimal(str(currency_settings['rate']))
                
                if min_price and min_price.strip():
                    converted_min = Decimal(min_price) / rate
                    queryset = queryset.filter(price__gte=converted_min)
                if max_price and max_price.strip():
                    converted_max = Decimal(max_price) / rate
                    queryset = queryset.filter(price__lte=converted_max)
            except (ValueError, decimal.InvalidOperation, TypeError):
                # If invalid price is provided, we just don't filter by price
                pass
        
        if size_filter:
            queryset = queryset.filter(sizes__name=size_filter)

        in_stock = self.request.GET.get('in_stock')
        if in_stock == '1':
            queryset = queryset.filter(stock__gt=0)

        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            queryset = queryset.order_by('-created')
            
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'store/product/product_list_fragment.html', context)
            
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['all_sizes'] = Size.objects.filter(products__in=Product.objects.filter(available=True)).distinct()
        context['price_range'] = Product.objects.filter(available=True).aggregate(Min('price'), Max('price'))
        context['current_filters'] = {
            'min_price': self.request.GET.get('min_price'),
            'max_price': self.request.GET.get('max_price'),
            'size': self.request.GET.get('size'),
            'sort': self.request.GET.get('sort'),
            'in_stock': self.request.GET.get('in_stock') == '1'
        }
        if self.request.user.is_authenticated:
            context['wishlist_product_ids'] = set(Wishlist.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        else:
            context['wishlist_product_ids'] = set()
        return context


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Trigger welcome email
            send_welcome_email.delay(user.id)
            login(request, user, backend='store.auth_backends.EmailOrUsernameModelBackend')
            return redirect('store:product_list')
    else:
        form = UserSignupForm()
    return render(request, 'store/accounts/signup.html', {'form': form})


@login_required
def profile(request):
    stats = dashboard_service.get_user_dashboard_stats(request.user)
    activities = dashboard_service.get_recent_activity(request.user)
    return render(request, 'store/accounts/profile.html', {
        'stats': stats,
        'activities': activities
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('store:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'store/accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/order/list.html', {'orders': orders})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    query_pk_and_slug = True

    def get_queryset(self):
        return Product.objects.filter(available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['form'] = ReviewForm()
        if self.request.user.is_authenticated:
            context['wishlist_product_ids'] = set(Wishlist.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        else:
            context['wishlist_product_ids'] = set()
        return context

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
            return redirect('store:product_detail', pk=product.id, slug=product.slug)
    return redirect('store:product_detail', pk=product.id, slug=product.slug)


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
        return redirect('store:product_detail', pk=product.id, slug=product.slug)

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
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
            try:
                profile = request.user.profile
                initial_data.update({
                    'phone': profile.phone,
                    'social_handle': profile.social_handle,
                    'city': profile.city,
                    'city_ref': profile.city_ref,
                    'warehouse': profile.warehouse,
                    'warehouse_ref': profile.warehouse_ref,
                })
            except AttributeError:
                pass
        form = OrderCreateForm(initial=initial_data)
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


def search_autocomplete(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(article__icontains=query),
        available=True
    )[:5]

    results = []
    for product in products:
        results.append({
            'name': product.name,
            'url': product.get_absolute_url(),
            'image': product.image.url if product.image else '/static/img/no-image.png',
            'price': str(product.price)
        })
    return JsonResponse({'results': results})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        action = 'removed'
    else:
        action = 'added'

    return JsonResponse({'status': 'ok', 'action': action})


class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'store/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

@require_POST
def set_currency(request):
    currency_code = request.POST.get('currency')
    if currency_code in [c['code'] for c in settings.CURRENCIES.values()]:
        request.session['currency'] = currency_code
    
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)

@require_POST
def set_preferences(request):
    language = request.POST.get('language')
    currency = request.POST.get('currency')
    next_url = request.POST.get('next', '/')
    
    if language in [lang[0] for lang in settings.LANGUAGES]:
        translation.activate(language)
        request.session['_language'] = language
        
        # Try to translate the next_url
        translated_url = translate_url(next_url, language)
        
        # If translate_url failed (returns same URL but it has a prefix of another language)
        # or if we just want to be extra safe, we ensure we don't redirect back to a conflicting prefix
        if translated_url == next_url and any(next_url.startswith(f"/{l}/") for l in [lang[0] for lang in settings.LANGUAGES] if l != language):
            # Fallback to home page with correct prefix if we can't translate reliably
             translated_url = f"/{language}/" if language != settings.LANGUAGE_CODE else "/"

        response = redirect(translated_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    else:
        response = redirect(next_url)

    if currency in [c['code'] for c in settings.CURRENCIES.values()]:
        request.session['currency'] = currency
    
    request.session['selection_made'] = True
    return response