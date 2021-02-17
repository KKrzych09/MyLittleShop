import braintree
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from io import BytesIO

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Getting nonce token
        nonce = request.POST.get('payment_method_nonce', None)
        # Creating and sending a transaction
        result = braintree.Transaction.sale({
            'amount' : '{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce' : nonce,
            'options' : {
                'submit_for_settlement' : True
            }
        })
        if result.is_success:
            # Marking an order as paid
            order.paid = True
            # Saving unique transacion ID
            order.braintree_id = result.transaction.id
            order.save()

            # Creating an email message which contains bill
            subject = 'My little shop - bill no. {}.'.format(order.id)
            message = 'For your last purchase, we have attached the bill.'
            email = EmailMessage(subject, message, 'admin@mylittleshop.com', [order.email])

            # Generating a PDF
            html = render_to_string('orders/order/pdf.html', {'order' : order})
            out = BytesIO()
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

            # Attaching a PDF file
            email.attach('order_{}.pdf'.format(order.id), out.getvalue(), 'application/pdf')

            # Sending email
            email.send()

            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # Generating a token
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                      'client_token': client_token})

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
