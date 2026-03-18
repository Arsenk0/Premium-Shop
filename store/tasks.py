from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    """
    Task to send an HTML e-mail notification when an order is successfully created.
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Замовлення №{order.id} - Підтвердження'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = order.email

        html_content = render_to_string('emails/order_confirmation.html', {'order': order})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Order.DoesNotExist:
        return False

@shared_task
def send_welcome_email(user_id):
    """
    Task to send a welcome email to a newly registered user.
    """
    try:
        user = User.objects.get(id=user_id)
        subject = f'Ласкаво просимо до нашого магазину, {user.username}!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = user.email

        if not to:
            return False

        html_content = render_to_string('emails/welcome.html', {'user': user})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except User.DoesNotExist:
        return False

@shared_task
def send_order_status_update_email(order_id):
    """
    Task to send an email when an order status changes.
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Оновлення статусу замовлення №{order.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = order.email

        html_content = render_to_string('emails/order_status_update.html', {'order': order})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Order.DoesNotExist:
        return False
