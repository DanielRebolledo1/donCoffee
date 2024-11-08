import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

from carts.models import CartItem
from .forms import PedidoForm
from .models import Pedido, Pago
# Create your views here.

def payments(request):
    if request.method == 'POST':
        num_pedido = request.POST.get('num_pedido')
        total_pedido = request.POST.get('total_pedido')

        relative_url = reverse('order_complete')
        full_url = request.build_absolute_uri(relative_url)
        tx = Transaction(
            WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
        response = tx.create(num_pedido, request.session.session_key, total_pedido, full_url)
        if 'url' in response and 'token' in response:
            urlTransbank = response['url'] + '?token_ws=' + response['token']
            return redirect(urlTransbank)
        else:
            return render(request, 'orders/payments.html')
    return render(request, 'orders/payments.html')


def place_order(request, total = 0, cantidad = 0):
    current_user = request.user
    
    #if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    iva = 0
    
    for cart_item in cart_items:
        total += (cart_item.producto.precio * cart_item.cantidad)
        cantidad += cart_item.cantidad
    
    iva = (19 * total) / 100
    grand_total = total
    subtotal = total - iva
        
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        
        if form.is_valid():
            data = Pedido()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.direccion = form.cleaned_data['direccion']
            data.ciudad = form.cleaned_data['ciudad']
            data.indicaciones = form.cleaned_data['indicaciones']
            data.nota_pedido = form.cleaned_data['nota_pedido']
            data.total_pedido = grand_total
            data.iva = iva
            data.subtotal = subtotal
            data.ip = request.META.get ('REMOTE_ADDR')
            data.save()
            #Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            num_pedido = current_date + str(data.id)
            data.num_pedido = num_pedido
            data.save()
            
            pedido = Pedido.objects.get(user = current_user, is_ordered = False, num_pedido = num_pedido)
            context = {
                'pedido': pedido,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'iva': iva,
                'total': total,
                'grand_total': grand_total
                
            }
            return render(request, 'orders/payments.html',context)
        else:
            return redirect('checkout')
    else:
        return redirect('checkout')


def order_complete(request):
    token = request.GET.get('token_ws')
    if not token:
        return redirect('home')

    tx = Transaction(
        WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.status(token)

    pedido = Pedido.objects.get(user=request.user, is_ordered=False, num_pedido=resp['buy_order'])

    pago = Pago()
    pago.pago_id = token
    pago.metodo_pago = 'Webpay'
    pago.monto_pagado = resp['amount']
    pago.estado = resp['vci']
    pago.user = request.user
    pago.save()

    pedido.pago = pago
    pedido.is_ordered = True
    pedido.save()

    if resp['vci'] == 'TSY':
        context = {
            pedido: pedido,
            pago: pago
        }

        return render(request, 'orders/order_complete.html', context)
    return render(request, 'orders/order_complete.html')