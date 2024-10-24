from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from store.models import Producto, Variante
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, producto_id):
    producto = Producto.objects.get(id=producto_id) #get the product
    producto_variation = []
    
    if request.method == 'POST':

        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variante.objects.get(producto=producto, variante_categoria__iexact=key,variante_value__iexact = value)
                producto_variation.append(variation)
            except:
                pass
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    is_cart_item_exist = CartItem.objects.filter(producto = producto, cart = cart).exists()
    
    if is_cart_item_exist:
        cart_item = CartItem.objects.filter(producto = producto, cart = cart)
        
        #existing variations -> database
        #current variation -> producto_variation
        #item_id -> database
        
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variantes.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
            
        print(ex_var_list)
        
        if producto_variation in ex_var_list:
            # increase the cart item quantity
            index = ex_var_list.index(producto_variation)
            item_id = id[index]
            item = CartItem.objects.get(producto = producto, id = item_id)
            item.cantidad += 1
            item.save()
     
        else:
            # create a new cart item
            item = CartItem.objects.create(producto = producto, cantidad = 1, cart = cart)
            
            if len(producto_variation) > 0:
                item.variantes.clear()
                item.variantes.add(*producto_variation)
                
            item.save()
        
    else:
        cart_item = CartItem.objects.create(
            producto = producto,
            cantidad = 1,
            cart = cart,
        )
        if len(producto_variation) > 0:
            cart_item.variantes.clear()
            cart_item.variantes.add(*producto_variation)
                
        cart_item.save()
    return redirect('cart')


def remove_cart(request, producto_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cart_item = CartItem.objects.get(producto = producto, cart = cart, id= cart_item_id)
        
        if cart_item.cantidad > 1:
            cart_item.cantidad -= 1
            cart_item.save()
        
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, producto_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    producto = get_object_or_404(Producto, id=producto_id)
    cart_item = CartItem.objects.get(producto = producto, cart = cart, id= cart_item_id)
    cart_item.delete()
    return redirect('cart')
    
    
def cart(request, total=0, cantidad=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            # Verifica si el cart_item tiene variantes asociadas
            if cart_item.variantes.exists():
                variante = cart_item.variantes.first()  # Obtiene la primera variante

                # Aplica la lógica en función del valor de la variante
                if variante.variante_value == 'Estandar':
                    total += cart_item.producto.precio * cart_item.cantidad
                elif variante.variante_value == 'Grande':
                    total += (cart_item.producto.precio + variante.variante_precio) * cart_item.cantidad
                elif variante.variante_value == 'Pequeño':
                    # Si es 'Pequeño', solo usa el precio base del producto
                    total += (cart_item.producto.precio - variante.variante_precio) * cart_item.cantidad
                else:
                    total += cart_item.producto.precio * cart_item.cantidad
            else:
                # Si no tiene variantes, usa el precio base del producto
                total += cart_item.producto.precio * cart_item.cantidad

            # Aumenta la cantidad total de productos
            cantidad += cart_item.cantidad

        # Calcula el IVA y el total general
        iva = (19 * total) / 100
        grand_total = total + iva

    except ObjectDoesNotExist:
        pass  # Ignorar si no existe el carrito

    # Preparar el contexto para pasar al template
    context = {
        'total': total,
        'cantidad': cantidad,
        'cart_items': cart_items,
        'iva': iva,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)
