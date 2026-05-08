"""
Utility functions for the Telegram bot.
"""
import django
import os

# Ensure Django is set up when this module is imported from outside Django context
def setup_django():
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
        django.setup()


def get_profile_by_chat_id(chat_id: int):
    """Return Profile instance for a given Telegram chat_id, or None."""
    from store.models import Profile
    try:
        return Profile.objects.select_related('user').get(telegram_chat_id=chat_id)
    except Profile.DoesNotExist:
        return None


def format_datetime(dt) -> str:
    """Format a datetime object to a readable Ukrainian string."""
    if dt is None:
        return "—"
    from django.utils import timezone
    local_dt = timezone.localtime(dt)
    return local_dt.strftime("%d.%m.%Y %H:%M")
