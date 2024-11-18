import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Q
from django.db.models import Count, Sum, F
from datetime import datetime as dt


from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

from carts.models import CartItem
from .forms import PedidoForm
from .models import Pedido, Pago, Pedido_producto
from store.models import Producto
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

    # Intenta obtener el pedido usando el número de orden
    try:
        pedido = Pedido.objects.get(user=request.user, is_ordered=False, num_pedido=resp['buy_order'])
    except Pedido.DoesNotExist:
        return redirect('home')

    # Crea un registro de pago
    pago = Pago(
        pago_id=token,
        metodo_pago='Webpay',
        monto_pagado=resp['amount'],
        estado=resp['vci'],
        user=request.user
    )
    pago.save()
    

    # Si el pago fue exitoso
    if resp['vci'] == 'TSY':
        pedido.pago = pago
        pedido.is_ordered = True
        pedido.estado = 'Completado'
        pedido.save()
        
        # Move the cart items to the table
        cart_items = CartItem.objects.filter(user = request.user)
        
        for item in cart_items:
            pedido_producto = Pedido_producto()
            pedido_producto.pedido =  pedido
            pedido_producto.pago = pago
            pedido_producto.user_id = request.user.id
            pedido_producto.producto_id = item.producto.id
            pedido_producto.cantidad = item.cantidad
            pedido_producto.precio_producto = item.producto.precio
            pedido_producto.ordered = True
            pedido_producto.save()
            
            #Para las variantes del producto en el caso de haber alguna
            cart_item = CartItem.objects.get(id = item.id)
            producto_variante = cart_item.variantes.all()
            pedido_producto.variantes.set(producto_variante)
            pedido_producto.save()
            
            #Reduce the quantity of the sold products
            producto = Producto.objects.get(id = item.producto_id)
            producto.stock -= item.cantidad
            producto.save()
        
        #clear cart
        CartItem.objects.filter(user = request.user).delete()
        
        # Envio de correo 
        mail_subject = 'Gracias por su compra'
        productos_pedido = Pedido_producto.objects.filter(pedido=pedido)
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'pedido': pedido,
            'pago': pago,
            'productos_pedido': productos_pedido,  # Pasamos los productos al contexto
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email])
        send_email.content_subtype = 'html'  # Especificamos el tipo de contenido como HTML
        send_email.send()
        
         # Obtén todos los productos del pedido
        productos_pedido = Pedido_producto.objects.filter(pedido=pedido)
        
        context = {
            'pedido': pedido,
            'pago': pago,
            'productos_pedido': productos_pedido,
        }
        return render(request, 'orders/order_complete.html', context)

    # Si el pago fue rechazado
    elif resp['vci'] == 'TSN':
        pedido.estado = 'Cancelado'
        pedido.save()

        return render(request, 'orders/order_failed.html', {'mensaje': 'El pago fue rechazado. Por favor, intente nuevamente.'})
    
    # Si hay otros estados de error o no manejados
    return redirect('home')


# Verifica si el usuario es administrador
def es_administrador(user):
    return user.is_staff

@user_passes_test(es_administrador)
def pedido_list(request):
    query = request.GET.get('q')  # Captura el término de búsqueda

    # Filtra los pedidos por el número si se ha ingresado un término de búsqueda
    if query:
        pedidos = Pedido.objects.filter(Q(num_pedido__icontains=query))
    else:
        pedidos = Pedido.objects.all()

    # Ordena y pagina los resultados
    pedidos = pedidos.order_by('-created_at')
    paginator = Paginator(pedidos, 10)
    page = request.GET.get('page')
    try:
        pedidos = paginator.page(page)
    except PageNotAnInteger:
        pedidos = paginator.page(1)
    except EmptyPage:
        pedidos = paginator.page(paginator.num_pages)

    return render(request, 'accounts/order_admin.html', {'pedidos': pedidos, 'query': query})


@user_passes_test(es_administrador)
def pedido_update_estado(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(pedido.ESTADO):  # Asegura que el nuevo estado es válido
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, 'Estado del pedido actualizado correctamente.')
        else:
            messages.error(request, 'Estado inválido.')
    return redirect('pedido_list')


@user_passes_test(es_administrador)
def pedido_delete(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    messages.success(request, 'Pedido eliminado correctamente.')
    return redirect('pedido_list')


def pedidos_grafico(request):
    # Filtrar los pedidos que están en estado 'completado'
    pedidos_completados = Pedido.objects.filter(estado='Completado')

    # Contar la cantidad de veces que cada producto ha sido comprado, solo para los pedidos completados
    productos_comprados = Pedido_producto.objects.filter(pedido__in=pedidos_completados) \
        .values('producto_id') \
        .annotate(total_compras=Sum('cantidad')) \
        .order_by('-total_compras')[:5]  # Obtener los 10 productos más comprados

    # Obtener los productos y las cantidades
    productos = Producto.objects.filter(id__in=[producto['producto_id'] for producto in productos_comprados])
    cantidades = [producto['total_compras'] for producto in productos_comprados]
    nombres_productos = [producto.nombre_producto for producto in productos]

    # Calcular el total de ventas correctamente (multiplicando el precio por la cantidad de productos)
    total_ventas = Pedido_producto.objects.filter(pedido__in=pedidos_completados) \
        .annotate(total_producto=F('precio_producto') * F('cantidad')) \
        .aggregate(total_ventas=Sum('total_producto'))['total_ventas'] or 0
        
        # Calcular total de ventas diarias
    hoy = dt.now().date()
    total_ventas_diarias = Pedido_producto.objects.filter(
        pedido__in=pedidos_completados,
        pedido__created_at__date=hoy
    ).annotate(total_producto=F('precio_producto') * F('cantidad')) \
        .aggregate(total_ventas=Sum('total_producto'))['total_ventas'] or 0

    # Calcular total de ventas mensuales
    mes_actual = dt.now().month
    total_ventas_mensuales = Pedido_producto.objects.filter(
        pedido__in=pedidos_completados,
        pedido__created_at__month=mes_actual
    ).annotate(total_producto=F('precio_producto') * F('cantidad')) \
        .aggregate(total_ventas=Sum('total_producto'))['total_ventas'] or 0

    # Ventas por día, solo para los pedidos completados
    ventas_por_dia = Pedido.objects.filter(estado='Completado') \
                                  .annotate(day=TruncDay('created_at')) \
                                  .values('day') \
                                  .annotate(total_ventas=Sum('total_pedido')) \
                                  .order_by('day')

    dias = [venta['day'].strftime('%d %b %Y') for venta in ventas_por_dia]
    ventas = [venta['total_ventas'] for venta in ventas_por_dia]

    # Productos más vendidos por categoría
    ventas_por_categoria = Pedido_producto.objects.filter(pedido__in=pedidos_completados) \
        .values('producto__categoria__nombre_categoria') \
        .annotate(total_categoria=Sum(F('cantidad') * F('precio_producto'))) \
        .order_by('-total_categoria')
        
    # Obtener los productos con mayor inventario y sus ventas
    productos_inventario = Producto.objects.all().order_by('-stock')[:10]
    productos_inventario_nombres = [producto.nombre_producto for producto in productos_inventario]
    productos_inventario_cantidades = [producto.stock for producto in productos_inventario]
    productos_ventas_cantidades = [
        Pedido_producto.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        for producto in productos_inventario
]

    nombres_categorias = [venta['producto__categoria__nombre_categoria'] for venta in ventas_por_categoria]
    ventas_categorias = [venta['total_categoria'] for venta in ventas_por_categoria]
    
    # Calcular ventas mensuales
    ventas_mensuales = pedidos_completados.annotate(month=TruncMonth('created_at')) \
                                           .values('month') \
                                           .annotate(total_ventas=Sum('total_pedido')) \
                                           .order_by('month')

    # Formatear los datos para el gráfico
    meses = [venta['month'].strftime('%b %Y') for venta in ventas_mensuales]
    ventas_totales = [venta['total_ventas'] for venta in ventas_mensuales]

    context = {
        'productos': nombres_productos,       # Nombres de los productos
        'cantidades': cantidades,             # Cantidades de compras
        'total_ventas': total_ventas,         # Total de ventas
        'dias': dias,                         # Fechas para el gráfico de ventas
        'ventas': ventas,                     # Ventas por día
        'nombres_categorias': nombres_categorias,  # Nombres de las categorías
        'ventas_categorias': ventas_categorias,    # Ventas por categoría
        'total_ventas_diarias': total_ventas_diarias,
        'total_ventas_mensuales': total_ventas_mensuales,
        'productos_inventario': productos_inventario_nombres,
        'cantidades_inventario': productos_inventario_cantidades,
        'cantidades_ventas': productos_ventas_cantidades,
        'meses': meses,
        'ventas_totales': ventas_totales,
    }

    return render(request, 'accounts/grafico.html', context)