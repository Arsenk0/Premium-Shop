from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Order, LoyaltyTransaction
from django.db import transaction
from django.utils.translation import gettext as _

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, points=25)
        LoyaltyTransaction.objects.create(
            user=instance,
            amount=25,
            action='registration',
            description=_('Бонус за реєстрацію')
        )

@receiver(post_save, sender=Order)
def order_completed(sender, instance, **kwargs):
    # Check if order is completed and user exists
    if instance.status == 'Completed' and instance.user:
        # Use a static (non-translated) key for deduplication so it is
        # language-agnostic — prevents double award if active language changes.
        description_key = f'Order #{instance.id}'
        if not LoyaltyTransaction.objects.filter(
            user=instance.user, action='purchase', description=description_key
        ).exists():
            total_cost = instance.get_total_cost()
            # 1 point for every 100 UAH
            points_to_add = int(total_cost // 100) * 1

            if points_to_add > 0:
                with transaction.atomic():
                    profile = instance.user.profile
                    profile.points += points_to_add
                    profile.save(update_fields=['points'])

                    LoyaltyTransaction.objects.create(
                        user=instance.user,
                        amount=points_to_add,
                        action='purchase',
                        description=description_key
                    )


@receiver(pre_save, sender=Order)
def track_order_status(sender, instance, **kwargs):
    """Cache the previous status before saving so post_save can detect changes."""
    if instance.pk:
        try:
            instance._previous_status = Order.objects.only('status').get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, created, **kwargs):
    """Send Telegram notification when order status changes after transaction commit."""
    if created:
        return  # No notification on creation — email handles confirmation

    previous_status = getattr(instance, '_previous_status', None)
    if previous_status is None or previous_status == instance.status:
        return  # Status didn't change

    if not instance.user:
        return  # Guest order, no Telegram notification

    from store.tasks import send_telegram_notification_sync
    import logging
    logger = logging.getLogger(__name__)

    def send_notification():
        try:
            # We use a thread to not block the main request, 
            # but we trigger it only on commit.
            import threading
            threading.Thread(
                target=send_telegram_notification_sync, 
                args=(instance.id,), 
                daemon=True
            ).start()
        except Exception as exc:
            logger.error("Error starting notification thread: %s", exc)

    transaction.on_commit(send_notification)
