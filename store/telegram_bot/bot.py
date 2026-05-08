"""
Main bot application setup for Premium Shop Telegram Bot.
Registers all handlers and provides the Application instance.
"""
import logging
import os

import django
from django.conf import settings as django_settings

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from store.telegram_bot.handlers.auth import start, get_auth_conversation_handler
from store.telegram_bot.handlers.orders import (
    orders_command, order_detail_command,
    orders_callback, order_callback,
)
from store.telegram_bot.handlers.loyalty import (
    loyalty_command, promo_command,
    loyalty_callback, promo_callback, promo_generate_callback,
)
from store.telegram_bot.handlers.common import (
    help_command, unlink_command,
    unlink_confirm_callback, unlink_cancel_callback,
    main_menu_callback, unknown_command,
)

logger = logging.getLogger(__name__)


def create_application() -> Application:
    """Build and configure the PTB Application."""
    token = django_settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in settings/environment!")

    app = Application.builder().token(token).build()

    # ── Conversation handler (OTP linking) — must be registered FIRST ──
    app.add_handler(get_auth_conversation_handler())

    # ── Commands ──
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("order", order_detail_command))
    app.add_handler(CommandHandler("loyalty", loyalty_command))
    app.add_handler(CommandHandler("promo", promo_command))
    app.add_handler(CommandHandler("unlink", unlink_command))

    # ── Inline Callbacks ──
    app.add_handler(CallbackQueryHandler(orders_callback, pattern='^orders$'))
    app.add_handler(CallbackQueryHandler(order_callback, pattern=r'^order_\d+$'))
    app.add_handler(CallbackQueryHandler(loyalty_callback, pattern='^loyalty$'))
    app.add_handler(CallbackQueryHandler(promo_callback, pattern='^promo$'))
    app.add_handler(CallbackQueryHandler(promo_generate_callback, pattern=r'^promo_(5|10)$'))
    app.add_handler(CallbackQueryHandler(unlink_confirm_callback, pattern='^unlink_confirm$'))
    app.add_handler(CallbackQueryHandler(unlink_cancel_callback, pattern='^unlink_cancel$'))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern='^main_menu$'))

    # ── Unknown commands fallback ──
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("✅ Premium Shop Bot handlers registered.")
    return app
