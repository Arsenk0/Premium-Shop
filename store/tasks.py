from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils.translation import gettext as _, override as translation_override
from .models import Order

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
