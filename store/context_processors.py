from store.cart import Cart

def cart_context(request):
    try:
        if hasattr(request, 'session'):
            cart = Cart(request)
            count = len(cart)
        else:
            count = 0
    except Exception:
        count = 0
    return {'cart_count': count}
def currency_context(request):
    selected_currency = request.session.get('currency')
    from django.conf import settings
    from django.utils.translation import get_language
    
    if not selected_currency:
        language = get_language()
        currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
        selected_currency = currency_settings['code']
    
    return {
        'selected_currency': selected_currency,
        'all_currencies': [c['code'] for c in settings.CURRENCIES.values()],
        'show_preferences_modal': not request.session.get('selection_made', False)
    }
