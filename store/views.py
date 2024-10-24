
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from category.models import Categoria
from carts.models import CartItem
from carts.views import _cart_id
from .models import Producto

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.
def store(request, categoria_slug = None):
    categorias = None
    productos = None
    
    if categoria_slug != None:
        categorias = get_object_or_404(Categoria, slug = categoria_slug)
        productos = Producto.objects.filter(categoria = categorias, disponible = True)
        paginator = Paginator(productos, 6)
        page = request.GET.get('page')
        paged_productos = paginator.get_page(page)
        productos_count = productos.count()
    else:
        productos = Producto.objects.all().filter(disponible=True).order_by('id')
        paginator = Paginator(productos, 6)
        page = request.GET.get('page')
        paged_productos = paginator.get_page(page)
        productos_count = productos.count()
    
    context = {
        'productos': paged_productos,
        'productos_count' : productos_count
    }
       
    return render(request, 'store/store.html', context)

def product_detail(request,categoria_slug, producto_slug):
    try:
        single_product = Producto.objects.get(categoria__slug=categoria_slug, slug = producto_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), producto = single_product).exists()
        
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            productos = Producto.objects.order_by('-fecha_creacion').filter(Q(descripcion__icontains=keyword)| Q(nombre_producto__icontains=keyword))
            productos_count = productos.count()
        context = {
            'productos': productos,
            'productos_count': productos_count,
        }
    return render(request, 'store/store.html', context)