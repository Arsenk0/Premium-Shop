from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Order, LoyaltyTransaction
from django.db import transaction
from django.utils.translation import gettext as _

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, points=50)
        LoyaltyTransaction.objects.create(
            user=instance,
            amount=50,
            action='registration',
            description=_('Бонус за реєстрацію')
        )

@receiver(post_save, sender=Order)
def order_completed(sender, instance, **kwargs):
    # Check if order is completed and user exists
    if instance.status == 'Completed' and instance.user:
        # We need to make sure we don't grant points multiple times for the same order.
        # Check if a transaction for this order already exists.
        description = _('Order') + f' #{instance.id}'
        if not LoyaltyTransaction.objects.filter(user=instance.user, action='purchase', description=description).exists():
            total_cost = instance.get_total_cost()
            # 5 points for every 100 UAH
            points_to_add = int(total_cost // 100) * 5
            
            if points_to_add > 0:
                with transaction.atomic():
                    profile = instance.user.profile
                    profile.points += points_to_add
                    profile.save(update_fields=['points'])
                    
                    LoyaltyTransaction.objects.create(
                        user=instance.user,
                        amount=points_to_add,
                        action='purchase',
                        description=description
                    )

# Order status signals removed as per user request to simplify email flow.
