def cart_context(request):
    cart = request.session.get('cart', {})
    try:
        count = sum(item.get('quantity', 0) if isinstance(item, dict) else 0 for item in cart.values())
    except Exception:
        count = 0
    return {'cart_count': count}
