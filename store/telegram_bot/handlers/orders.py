"""
Orders handlers: /orders, /order <id>, inline callbacks.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from store.telegram_bot import messages as msg
from store.telegram_bot.keyboards import get_orders_keyboard, get_order_detail_keyboard, get_main_menu_keyboard
from store.telegram_bot.utils import get_profile_by_chat_id, format_datetime

logger = logging.getLogger(__name__)


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /orders command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await update.message.reply_html(msg.NOT_LINKED)
        return

    await _send_orders_list(update, context, profile, use_edit=False)


async def order_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order <id> command."""
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await update.message.reply_html(msg.NOT_LINKED)
        return

    if not context.args:
        await update.message.reply_text("Вкажіть ID замовлення: /order 123")
        return

    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Невірний ID замовлення.")
        return

    await _send_order_detail(update, context, profile, order_id, use_edit=False)


async def orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'orders' inline callback."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')
        return

    await _send_orders_list(update, context, profile, use_edit=True)


async def order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'order_<id>' inline callback."""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split('_')[1])
    chat_id = update.effective_user.id
    profile = await _get_profile(chat_id)

    if not profile:
        await query.edit_message_text(msg.NOT_LINKED, parse_mode='HTML')
        return

    await _send_order_detail(update, context, profile, order_id, use_edit=True)


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _get_profile(chat_id: int):
    from asgiref.sync import sync_to_async
    return await sync_to_async(get_profile_by_chat_id)(chat_id)


async def _send_orders_list(update, context, profile, use_edit: bool):
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _fetch_orders(user):
        from store.models import Order
        return list(
            Order.objects.filter(user=user)
            .order_by('-created')[:5]
            .values('id', 'status', 'created')
        )

    @sync_to_async
    def _get_total(order_id):
        from store.models import Order
        try:
            order = Order.objects.get(id=order_id)
            return order.get_total_cost()
        except Order.DoesNotExist:
            return 0

    orders = await _fetch_orders(profile.user)

    if not orders:
        text = msg.NO_ORDERS
        keyboard = get_main_menu_keyboard()
        if use_edit:
            await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_html(text, reply_markup=keyboard)
        return

    text = msg.ORDER_LIST_HEADER
    for order in orders:
        icon = msg.ORDER_STATUS_ICONS.get(order['status'], '📦')
        status_name = msg.ORDER_STATUS_NAMES.get(order['status'], order['status'])
        total = await _get_total(order['id'])
        text += msg.ORDER_LIST_ITEM.format(
            icon=icon,
            order_id=order['id'],
            status=status_name,
            total=total,
            date=format_datetime(order['created']),
        )

    keyboard = get_orders_keyboard([o['id'] for o in orders])

    if use_edit:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.message.reply_html(text, reply_markup=keyboard)


async def _send_order_detail(update, context, profile, order_id: int, use_edit: bool):
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _fetch_order(user, oid):
        from store.models import Order
        try:
            order = Order.objects.prefetch_related('items__product').get(id=oid, user=user)
            return order
        except Order.DoesNotExist:
            return None

    order = await _fetch_order(profile.user, order_id)

    if not order:
        text = msg.ORDER_NOT_FOUND.format(order_id=order_id)
        keyboard = get_orders_keyboard([])
        if use_edit:
            await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_html(text, reply_markup=keyboard)
        return

    icon = msg.ORDER_STATUS_ICONS.get(order.status, '📦')
    status_name = msg.ORDER_STATUS_NAMES.get(order.status, order.status)

    # Build items list
    items_text = ""
    for item in order.items.all():
        size_str = f" ({item.size})" if item.size else ""
        items_text += msg.ORDER_ITEM_LINE.format(
            name=item.product.name,
            size=size_str,
            qty=item.quantity,
            price=item.price * item.quantity,
        )

    text = msg.ORDER_DETAIL.format(
        order_id=order.id,
        icon=icon,
        status=status_name,
        total=order.get_total_cost(),
        date=format_datetime(order.created),
        city=order.city,
        warehouse=order.warehouse,
        items=items_text,
    )

    keyboard = get_order_detail_keyboard(order_id)

    if use_edit:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.message.reply_html(text, reply_markup=keyboard)
