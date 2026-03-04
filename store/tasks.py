from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    """
    Task to send an e-mail notification when an order is successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Замовлення №{order.id}'
    message = f'Шановний/а {order.first_name},\n\n' \
              f'Ви успішно оформили замовлення в нашому магазині.\n' \
              f'Номер вашого замовлення: {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@shop.com',
                          [order.email])
    return mail_sent
