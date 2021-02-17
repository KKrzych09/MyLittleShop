from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def order_created(order_id):
    """
    A task which sends notification via email 
    after successfully created order object.
    """
    order = Order.objects.get(id=order_id)
    subject = 'Order no. {}'.format(order.id)
    message = 'Hello, {}!\n\nYou have placed an order in our shop.\
                    Order ID: {}.'.format(order.first_name, order.id)
    
    mail_sent = send_mail(subject,
                          message,
                          'admin@mylittleshop.com',
                          [order.email])
    return mail_sent
