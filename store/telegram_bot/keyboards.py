"""
Keyboard builders for Premium Shop Telegram Bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


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
    """Promo choice keyboard."""
    buttons = []
    if points >= 250:
        buttons.append([InlineKeyboardButton("🥈 250 балів → 5% знижка", callback_data="promo_5")])
    if points >= 600:
        buttons.append([InlineKeyboardButton("🥇 600 балів → 10% знижка", callback_data="promo_10")])
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
