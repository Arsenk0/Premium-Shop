"""
Keyboard builders for Premium Shop Telegram Bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from django.utils.translation import gettext as _
from store.telegram_bot import messages as msg


def get_start_keyboard(linked: bool) -> InlineKeyboardMarkup:
    """Keyboard for /start command."""
    if linked:
        buttons = [
            [InlineKeyboardButton("📦 Мої замовлення", callback_data="orders")],
            [InlineKeyboardButton("🎁 Бонусні бали", callback_data="loyalty")],
            [InlineKeyboardButton("🎟 Отримати промокод", callback_data="promo")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton("🔗 Ввести код прив'язки", callback_data="enter_otp")],
        ]
    return InlineKeyboardMarkup(buttons)


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Main persistent menu at the bottom."""
    buttons = [
        [KeyboardButton(str(msg.BTN_ORDERS)), KeyboardButton(str(msg.BTN_LOYALTY))],
        [KeyboardButton(str(msg.BTN_PROMO)), KeyboardButton(str(msg.BTN_PROFILE))],
        [KeyboardButton(str(msg.BTN_SUPPORT))],
    ]
    return ReplyKeyboardMarkup(
        buttons, 
        resize_keyboard=True, 
        is_persistent=True,
        input_field_placeholder=str(_("Оберіть розділ меню..."))
    )


def get_order_detail_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Back button from order detail."""
    buttons = [
        [InlineKeyboardButton("◀️ До списку замовлень", callback_data="orders")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_orders_keyboard(order_ids: list) -> InlineKeyboardMarkup:
    """Keyboard with order detail buttons."""
    buttons = [
        [InlineKeyboardButton(f"📋 Деталі замовлення #{oid}", callback_data=f"order_{oid}")]
        for oid in order_ids
    ]
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def get_promo_keyboard(points: int) -> InlineKeyboardMarkup:
    """Promo choice keyboard with new tiers."""
    buttons = []
    if points >= 200:
        buttons.append([InlineKeyboardButton("🥉 200 балів → 5% знижка", callback_data="promo_5")])
    if points >= 500:
        buttons.append([InlineKeyboardButton("🥈 500 балів → 7% знижка", callback_data="promo_7")])
    if points >= 1000:
        buttons.append([InlineKeyboardButton("🥇 1000 балів → 10% знижка", callback_data="promo_10")])
    if points >= 2000:
        buttons.append([InlineKeyboardButton("💎 2000 балів → 12% знижка", callback_data="promo_12")])
    if points >= 5000:
        buttons.append([InlineKeyboardButton("👑 5000 балів → 15% знижка", callback_data="promo_15")])
    
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def get_unlink_keyboard() -> InlineKeyboardMarkup:
    """Confirmation keyboard for unlink."""
    buttons = [
        [
            InlineKeyboardButton("✅ Так, від'єднати", callback_data="unlink_confirm"),
            InlineKeyboardButton("❌ Скасувати", callback_data="unlink_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    buttons = [
        [InlineKeyboardButton("📦 Мої замовлення", callback_data="orders")],
        [InlineKeyboardButton("🎁 Бонусні бали", callback_data="loyalty")],
        [InlineKeyboardButton("🎟 Отримати промокод", callback_data="promo")],
    ]
    return InlineKeyboardMarkup(buttons)
