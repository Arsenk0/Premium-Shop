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
