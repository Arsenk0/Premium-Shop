"""
Loyalty handlers: /loyalty, /promo, promo generation via inline callbacks.
"""
import logging
import string
import random
from telegram import Update
from telegram.ext import ContextTypes

from store.telegram_bot import messages as msg
from store.telegram_bot.keyboards import get_promo_keyboard, get_main_menu_keyboard
from store.telegram_bot.utils import get_profile_by_chat_id, format_datetime

logger = logging.getLogger(__name__)


async def loyalty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /loyalty command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await update.message.reply_html(msg.NOT_LINKED)
        return

    await _send_loyalty_info(update, context, profile, use_edit=False)


async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /promo command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await update.message.reply_html(msg.NOT_LINKED)
        return

    await _send_promo_menu(update, context, profile, use_edit=False)


async def loyalty_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'loyalty' inline callback."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')
        return

    await _send_loyalty_info(update, context, profile, use_edit=True)


async def promo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'promo' inline callback."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')
        return

    await _send_promo_menu(update, context, profile, use_edit=True)


async def promo_generate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'promo_5' or 'promo_10' inline callback to generate coupon."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')
        return

    tier = query.data.split('_')[1]  # '5' or '10'
    result = await _generate_coupon(profile, tier)

    if result == 'insufficient':
        await query.edit_message_text(
            msg.PROMO_NOT_ENOUGH.format(points=profile.user.profile.points),
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )
    elif result == 'invalid_tier':
        await query.edit_message_text("❌ Невірний варіант.", parse_mode='HTML')
    else:
        code, discount, valid_to = result
        await query.edit_message_text(
            msg.PROMO_GENERATED.format(
                code=code,
                discount=discount,
                valid_to=valid_to,
            ),
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _get_profile(chat_id: int):
    from asgiref.sync import sync_to_async
    return await sync_to_async(get_profile_by_chat_id)(chat_id)


async def _get_fresh_profile(chat_id: int):
    """Re-fetch profile to get current points."""
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _fetch():
        from store.models import Profile
        try:
            return Profile.objects.select_related('user').get(telegram_chat_id=chat_id)
        except Profile.DoesNotExist:
            return None
    return await _fetch()


async def _send_loyalty_info(update, context, profile, use_edit: bool):
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _get_points(p):
        p.refresh_from_db(fields=['points'])
        return p.points

    points = await _get_points(profile)

    if points < 250:
        tier = msg.LOYALTY_TIER_BRONZE
        progress = int((points / 250) * 100)
    elif points < 600:
        tier = msg.LOYALTY_TIER_SILVER
        progress = int(((points - 250) / (600 - 250)) * 100)
    else:
        tier = msg.LOYALTY_TIER_GOLD
        progress = 100

    text = msg.LOYALTY_INFO.format(points=points, tier=tier, progress=progress)

    if use_edit:
        await update.callback_query.edit_message_text(
            text, parse_mode='HTML', reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_html(text, reply_markup=get_main_menu_keyboard())


async def _send_promo_menu(update, context, profile, use_edit: bool):
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _get_points(p):
        p.refresh_from_db(fields=['points'])
        return p.points

    points = await _get_points(profile)

    if points < 250:
        text = msg.PROMO_NOT_ENOUGH.format(points=points)
        keyboard = get_main_menu_keyboard()
    else:
        text = msg.PROMO_CHOOSE_TIER.format(points=points)
        keyboard = get_promo_keyboard(points)

    if use_edit:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.message.reply_html(text, reply_markup=keyboard)


async def _generate_coupon(profile, tier: str):
    """Generate a coupon for the given tier. Returns (code, discount, valid_to_str) or error string."""
    from asgiref.sync import sync_to_async

    conversion_rules = {
        '5': {'points': 250, 'discount': 5},
        '10': {'points': 600, 'discount': 10},
    }

    if tier not in conversion_rules:
        return 'invalid_tier'

    rule = conversion_rules[tier]

    @sync_to_async
    def _do():
        from store.models import Profile, Coupon, LoyaltyTransaction
        from django.utils import timezone
        from django.db import transaction as db_transaction

        try:
            fresh_profile = Profile.objects.select_related('user').get(pk=profile.pk)
        except Profile.DoesNotExist:
            return 'insufficient'

        if fresh_profile.points < rule['points']:
            return 'insufficient'

        with db_transaction.atomic():
            fresh_profile.points -= rule['points']
            fresh_profile.save(update_fields=['points'])

            code = f"TG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            valid_from = timezone.now()
            valid_to = valid_from + timezone.timedelta(days=30)

            Coupon.objects.create(
                code=code,
                valid_from=valid_from,
                valid_to=valid_to,
                discount=rule['discount'],
                active=True,
                user=fresh_profile.user,
            )

            LoyaltyTransaction.objects.create(
                user=fresh_profile.user,
                amount=-rule['points'],
                action='conversion',
                description=f"Конвертація через Telegram-бот: {code} ({rule['discount']}%)",
            )

        return (code, rule['discount'], valid_to.strftime('%d.%m.%Y'))

    return await _do()
