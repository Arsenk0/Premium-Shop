"""
Auth handlers: /start, OTP linking, conversation flow.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from store.telegram_bot import messages as msg
from store.telegram_bot.keyboards import get_start_keyboard, get_main_menu_keyboard
from store.telegram_bot.utils import get_profile_by_chat_id, format_datetime

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_OTP = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if profile:
        text = msg.WELCOME_LINKED.format(username=profile.user.username)
        await update.message.reply_html(text, reply_markup=get_start_keyboard(linked=True))
    else:
        await update.message.reply_html(msg.WELCOME_UNLINKED, reply_markup=get_start_keyboard(linked=False))


async def prompt_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to enter the OTP from the website."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if profile:
        await query.edit_message_text(
            msg.ALREADY_LINKED.format(username=profile.user.username),
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END

    await query.edit_message_text(msg.ENTER_OTP, parse_mode='HTML')
    return WAITING_FOR_OTP


async def handle_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify OTP and link the account."""
    from asgiref.sync import sync_to_async
    from django.utils import timezone

    token = update.message.text.strip()
    chat_id = update.effective_user.id

    profile = await _verify_and_link(token, chat_id)

    if profile:
        await update.message.reply_html(
            msg.LINK_SUCCESS.format(username=profile.user.username),
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_html(msg.LINK_INVALID_TOKEN)
        return WAITING_FOR_OTP


async def cancel_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the OTP conversation."""
    await update.message.reply_text("↩️ Прив'язку скасовано.")
    return ConversationHandler.END


# ─── Sync ORM helpers wrapped with sync_to_async ─────────────────────────────

async def _get_profile(chat_id: int):
    from asgiref.sync import sync_to_async
    return await sync_to_async(get_profile_by_chat_id)(chat_id)


async def _verify_and_link(token: str, chat_id: int):
    """Verify OTP token and link chat_id to profile. Returns profile or None."""
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _do():
        from store.models import Profile
        from django.utils import timezone
        import datetime

        try:
            profile = Profile.objects.select_related('user').get(telegram_link_token=token)
        except Profile.DoesNotExist:
            return None

        # Check token expiry (10 minutes)
        if profile.telegram_token_created:
            age = timezone.now() - profile.telegram_token_created
            if age > datetime.timedelta(minutes=10):
                return None

        profile.telegram_chat_id = chat_id
        profile.telegram_link_token = ''
        profile.telegram_token_created = None
        profile.save(update_fields=['telegram_chat_id', 'telegram_link_token', 'telegram_token_created'])
        return profile

    return await _do()


def get_auth_conversation_handler():
    """Return the ConversationHandler for OTP linking."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(prompt_otp, pattern='^enter_otp$')],
        states={
            WAITING_FOR_OTP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_otp)],
    )
