from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from category.models import Categoria
from carts.models import CartItem
from carts.views import _cart_id
from .models import Producto, ReviewRating
from orders.models import Pedido_producto
from .forms import ProductoForm, ReviewForm
from django.contrib.auth.decorators import user_passes_test

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

    if request.user.is_authenticated:
        try:
            orderproduct = Pedido_producto.objects.filter(user = request.user, producto_id = single_product.id).exists()
            
        except Pedido_producto.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    #get the reviews
    reviews = ReviewRating.objects.filter(producto_id = single_product.id, status = True)
    
    # Calcular el promedio de reseñas
    average_review = single_product.averageReview()
    # Calculamos el número de estrellas
    full_stars = int(average_review)  # Número de estrellas completas
    half_star = 1 if average_review - full_stars >= 0.5 else 0  # Si hay media estrella
    empty_stars = 5 - full_stars - half_star  # Estrellas vacías

    # Generamos la lista de clases de estrellas
    stars = (['fas fa-star'] * full_stars + 
             ['fas fa-star-half-alt'] * half_star + 
             ['far fa-star'] * empty_stars)


    for review in reviews:
        full_stars = int(review.rating)  # Número de estrellas completas
        half_star = 1 if review.rating - full_stars >= 0.5 else 0  # Si hay media estrella
        empty_stars = 5 - full_stars - half_star  # Estrellas vacías

        # Genera una lista con las clases de icono para cada estrella
        review.stars = (['fas fa-star'] * full_stars + 
                        ['fas fa-star-half-alt'] * half_star + 
                        ['far fa-star'] * empty_stars)
        
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'average_review': average_review,
        'stars': stars,
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


# ADMINISTRATOR

def is_admin(user):
    return user.is_authenticated and user.is_staff  # user.is_staff es True para usuarios administradores

@user_passes_test(is_admin)
# Lista de productos
def producto_list(request):
    productos = Producto.objects.all()
    context = {'productos': productos}
    return render(request, 'administrator/producto_list.html', context)


@user_passes_test(is_admin)
# Crear producto
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Producto creado exitosamente.')
                return redirect('producto_list')
            except ValidationError as e:
                form.add_error(None, e)
                messages.error(request, str(e))
        else:
            messages.error(request, 'Error al crear el producto. Revisa los campos.')
    else:
        form = ProductoForm()
    
    return render(request, 'administrator/producto_form.html', {'form': form})

@user_passes_test(is_admin)
# Actualizar producto
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'administrator/producto_form.html', {'form': form})


@user_passes_test(is_admin)
# Eliminar producto
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('producto_list')
    return render(request, 'administrator/producto_confirm_delete.html', {'producto': producto})


def submit_review(request, producto_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id, producto__id = producto_id)
            form = ReviewForm(request.POST, instance=reviews)
            
            form.save()
            messages.success(request, 'Gracias!, Su reseña ha sido actualizada')
            
            return redirect(url)
            
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.producto_id = producto_id
                data.user_id = request.user.id
                data.save()
                
                messages.success(request, 'Gracias!, Su reseña se ha guardado con éxito')
                
                return redirect(url)