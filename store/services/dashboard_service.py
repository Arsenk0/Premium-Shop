from django.db.models import Sum, Count
from ..models import Order, Review, Wishlist
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

def get_user_dashboard_stats(user):
    """
    Returns statistics for the user dashboard.
    """
    stats = {
        'total_orders': Order.objects.filter(user=user).count(),
        'total_spent': Order.objects.filter(user=user, status='Completed').aggregate(total=Sum('items__price'))['total'] or 0,
        'wishlist_count': Wishlist.objects.filter(user=user).count(),
        'reviews_count': Review.objects.filter(user=user).count(),
    }
    return stats

def get_recent_activity(user, limit=5):
    """
    Returns a combined list of recent activities for the user.
    """
    activities = []
    
    # Recent Orders
    orders = Order.objects.filter(user=user).order_by('-created')[:limit]
    for order in orders:
        status_colors = {
            'New': '#17a2b8',
            'Processing': '#ffc107',
            'Shipped': '#007bff',
            'Delivered': '#28a745',
            'Cancelled': '#dc3545'
        }
        color = status_colors.get(order.status, '#6c757d')
        activities.append({
            'type': 'order',
            'date': order.created,
            'title': _('Замовлення') + f' #{order.id}',
            'description': f"{_('Статус')}: <span style='color: {color}; font-weight: 600;'>{order.get_status_display()}</span>",
            'icon': '📦'
        })
        
    # Recent Reviews
    reviews = Review.objects.filter(user=user).order_by('-created_at')[:limit]
    for review in reviews:
        activities.append({
            'type': 'review',
            'date': review.created_at,
            'title': _('Відгук на') + f' {review.product.name}',
            'description': _('Оцінка:') + f' {review.rating}/5',
            'icon': '⭐'
        })
        
    # Recent Wishlist additions
    wishlist_items = Wishlist.objects.filter(user=user).order_by('-added_at')[:limit]
    for item in wishlist_items:
        activities.append({
            'type': 'wishlist',
            'date': item.added_at,
            'title': _('Додано в обране:') + f' {item.product.name}',
            'description': _('Будемо чекати на ваше замовлення!'),
            'icon': '❤️'
        })
        
    # Sort activities by date descending
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return activities[:limit]
