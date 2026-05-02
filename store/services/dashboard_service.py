from django.db.models import Sum, Count, F
from ..models import Order, Review, Wishlist, LoyaltyTransaction
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.urls import reverse

def get_user_dashboard_stats(user):
    """
    Returns statistics for the user dashboard.
    """
    stats = {
        'total_orders': Order.objects.filter(user=user).count(),
        'total_spent': Order.objects.filter(user=user, status='Completed').aggregate(
            total=Sum(F('items__price') * F('items__quantity'))
        )['total'] or 0,
        'wishlist_count': Wishlist.objects.filter(user=user).count(),
        'reviews_count': Review.objects.filter(user=user).count(),
    }
    return stats

def get_recent_activity(user, limit=10):
    """
    Returns a combined list of recent activities for the user.
    """
    activities = []
    
    STATUS_COLORS = {
        'New': '#17a2b8',
        'Processing': '#ffc107',
        'Shipped': '#007bff',
        'Completed': '#28a745',
        'Canceled': '#dc3545'
    }
    
    LOYALTY_ICONS = {
        'registration': 'fas fa-user-plus',
        'purchase': 'fas fa-shopping-bag',
        'review': 'fas fa-comment-alt',
        'conversion': 'fas fa-ticket-alt',
    }
    
    # Recent Orders
    orders = Order.objects.filter(user=user).order_by('-created')[:limit]
    for order in orders:
        activities.append({
            'type': 'order',
            'date': order.created,
            'title': _('Order') + f' #{order.id}',
            'description': _('Статус') + ': ' + order.get_status_display(),
            'status_color': STATUS_COLORS.get(order.status, '#6c757d'),
            'icon_class': 'fas fa-box',
            'url': reverse('store:order_success', kwargs={'order_id': order.id}),
        })
        
    # Recent Reviews
    reviews = Review.objects.filter(user=user).order_by('-created_at')[:limit]
    for review in reviews:
        activities.append({
            'type': 'review',
            'date': review.created_at,
            'title': _('Відгук на') + f' {review.product.name}',
            'description': _('Оцінка:') + f' {review.rating}/5',
            'icon_class': 'fas fa-star',
            'url': reverse('store:product_detail', kwargs={'pk': review.product.id, 'slug': review.product.slug}),
        })
        
    # Recent Wishlist additions
    wishlist_items = Wishlist.objects.filter(user=user).order_by('-added_at')[:limit]
    for item in wishlist_items:
        activities.append({
            'type': 'wishlist',
            'date': item.added_at,
            'title': _('Додано в обране:') + f' {item.product.name}',
            'description': _('Будемо чекати на ваше замовлення!'),
            'icon_class': 'fas fa-heart',
            'url': reverse('store:product_detail', kwargs={'pk': item.product.id, 'slug': item.product.slug}),
        })
        
    # Recent Loyalty Transactions
    loyalty_txs = LoyaltyTransaction.objects.filter(user=user).order_by('-created_at')[:limit]
    for tx in loyalty_txs:
        points_str = f"{'+' if tx.amount > 0 else ''}{tx.amount} " + _('балів')

        # Purchase descriptions are stored as static 'Order #N' (language-agnostic key
        # used for deduplication). Reconstruct the translated version at display time.
        if tx.action == 'purchase' and tx.description.startswith('Order #'):
            order_num = tx.description[len('Order #'):]
            display_description = _('Order') + f' #{order_num}'
        else:
            display_description = tx.description

        activities.append({
            'type': 'loyalty',
            'date': tx.created_at,
            'title': tx.get_action_display(),
            'description': display_description,
            'points': tx.amount,
            'points_display': points_str,
            'icon_class': LOYALTY_ICONS.get(tx.action, 'fas fa-gem'),
            'url': reverse('store:loyalty_details'),
        })

    # Sort activities by date descending
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return activities[:limit]


def get_spending_data(user):
    """
    Returns monthly spending data for the user (after discounts).
    Uses Python-side aggregation to correctly apply discount_amount,
    keeping consistency with Order.get_total_cost().
    """
    from django.db.models import Sum, F
    from decimal import Decimal

    orders = Order.objects.filter(
        user=user,
        status='Completed'
    ).prefetch_related('items').order_by('created__year', 'created__month')

    # Aggregate by (year, month) in Python to correctly subtract discount_amount
    monthly = {}
    for order in orders:
        key = (order.created.year, order.created.month)
        if key not in monthly:
            monthly[key] = Decimal('0')
        monthly[key] += order.get_total_cost()

    result = [
        {'year': year, 'month': month, 'total': total}
        for (year, month), total in sorted(monthly.items())
    ]
    return result
