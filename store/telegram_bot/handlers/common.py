"""
Common handlers: /help, /unlink, main_menu callback, unknown commands.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from store.telegram_bot import messages as msg
from store.telegram_bot.keyboards import get_unlink_keyboard, get_start_keyboard, get_main_menu_keyboard
from store.telegram_bot.utils import get_profile_by_chat_id

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_html(msg.HELP_TEXT)


async def unlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unlink command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await update.message.reply_html(msg.NOT_LINKED)
        return

    await update.message.reply_html(
        msg.UNLINK_CONFIRM.format(username=profile.user.username),
        reply_markup=get_unlink_keyboard()
    )


async def unlink_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm unlinking the account."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id

    success = await _do_unlink(chat_id)
    if success:
        await query.edit_message_text(msg.UNLINK_SUCCESS, parse_mode='HTML')
    else:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')


async def unlink_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel unlinking."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(msg.UNLINK_CANCELLED, parse_mode='HTML', reply_markup=get_main_menu_keyboard())


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if profile:
        text = msg.WELCOME_LINKED.format(username=profile.user.username)
        keyboard = get_start_keyboard(linked=True)
    else:
        text = msg.WELCOME_UNLINKED
        keyboard = get_start_keyboard(linked=False)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Невідома команда. Використайте /help для перегляду доступних команд."
    )


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _get_profile(chat_id: int):
    from asgiref.sync import sync_to_async
    return await sync_to_async(get_profile_by_chat_id)(chat_id)


async def _do_unlink(chat_id: int) -> bool:
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _unlink():
        from store.models import Profile
        updated = Profile.objects.filter(telegram_chat_id=chat_id).update(
            telegram_chat_id=None,
            telegram_link_token='',
            telegram_token_created=None,
        )
        return updated > 0

    return await _unlink()
