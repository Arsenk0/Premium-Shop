from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils.translation import gettext as _, override as translation_override
from .models import Order
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation_email(order_id, language='uk', currency='UAH', base_url=None):
    """
    Task to send an HTML e-mail notification when an order is successfully created.
    """
    try:
        order = Order.objects.get(id=order_id)
        with translation_override(language):
            subject = _('Замовлення №%(order_id)s - Підтвердження') % {'order_id': order.id}
            from_email = settings.DEFAULT_FROM_EMAIL
            to = order.email

            html_content = render_to_string('emails/order_confirmation.html', {
                'order': order,
                'currency': currency,
                'base_url': base_url
            })
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            
            # Generate PDF
            import weasyprint
            pdf_html = render_to_string('emails/invoice_pdf.html', {
                'order': order,
                'currency': currency,
                'base_url': base_url
            })
            pdf = weasyprint.HTML(string=pdf_html).write_pdf()
            
            # Attach PDF
            msg.attach(f'invoice_{order.id}.pdf', pdf, 'application/pdf')
            
            msg.send()
        return True
    except Order.DoesNotExist:
        return False

@shared_task
def send_welcome_email(user_id, language='uk', currency='UAH', base_url=None):
    """
    Task to send a welcome email to a newly registered user.
    """
    try:
        user = User.objects.get(id=user_id)
        with translation_override(language):
            subject = _('Ласкаво просимо до нашого магазину, %(username)s!') % {'username': user.username}
            from_email = settings.DEFAULT_FROM_EMAIL
            to = user.email

            if not to:
                return False

            html_content = render_to_string('emails/welcome.html', {
                'user': user,
                'currency': currency,
                'base_url': base_url
            })
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return True
    except User.DoesNotExist:
        return False

@shared_task
def send_order_status_update_email(order_id, language='uk', currency='UAH', base_url=None):
    """
    Task to send an email when an order status changes.
    """
    try:
        order = Order.objects.get(id=order_id)
        with translation_override(language):
            subject = _('Оновлення статусу замовлення №%(order_id)s') % {'order_id': order.id}
            from_email = settings.DEFAULT_FROM_EMAIL
            to = order.email

            html_content = render_to_string('emails/order_status_update.html', {
                'order': order,
                'currency': currency,
                'base_url': base_url
            })
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return True
    except Order.DoesNotExist:
        return False


@shared_task
def send_telegram_status_notification(order_id):
    """
    Send an order status update notification via Telegram bot.
    Called by the order post_save signal when status changes.
    """
    try:
        order = Order.objects.select_related('user__profile').get(id=order_id)
    except Order.DoesNotExist:
        logger.warning("send_telegram_status_notification: Order %s not found", order_id)
        return False

    if not order.user:
        return False

    try:
        profile = order.user.profile
    except Exception:
        return False

    chat_id = profile.telegram_chat_id
    if not chat_id:
        logger.debug(
            "send_telegram_status_notification: user %s has no telegram_chat_id",
            order.user.username
        )
        return False

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("send_telegram_status_notification: TELEGRAM_BOT_TOKEN not set")
        return False

    from store.telegram_bot.messages import (
        STATUS_NOTIFICATION, STATUS_EXTRA,
        ORDER_STATUS_ICONS, ORDER_STATUS_NAMES,
    )
    from django.utils import timezone

    icon = ORDER_STATUS_ICONS.get(order.status, '📦')
    status_name = ORDER_STATUS_NAMES.get(order.status, order.status)
    extra = STATUS_EXTRA.get(order.status, '')

    local_updated = timezone.localtime(order.updated)
    text = STATUS_NOTIFICATION.format(
        order_id=order.id,
        icon=icon,
        status=status_name,
        total=order.get_total_cost(),
        updated=local_updated.strftime('%d.%m.%Y %H:%M'),
        extra_message=extra,
    )

    import asyncio
    import telegram

    async def _send():
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')

    try:
        asyncio.run(_send())
        logger.info(
            "Telegram notification sent to chat_id=%s for order #%s (status=%s)",
            chat_id, order.id, order.status
        )
        return True
    except Exception as exc:
        logger.error(
            "Failed to send Telegram notification for order #%s: %s",
            order.id, exc
        )
        return False
