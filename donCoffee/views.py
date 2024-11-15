from django.shortcuts import render
from store.models import Producto, ReviewRating

def home(request):
    productos = Producto.objects.all().filter(disponible=True).order_by('fecha_creacion')[:8]  # Limitar a 6 productos inicialmente
    
    # Lista para almacenar los productos y sus estrellas
    productos_con_estrellas = []

    for producto in productos:
        # Obtener las reseñas del producto
        reviews = ReviewRating.objects.filter(producto_id=producto.id, status=True)
        
        # Calcular el promedio de las reseñas del producto
        if reviews.exists():
            average_review = producto.averageReview()
            full_stars = int(average_review)  # Número de estrellas completas
            half_star = 1 if average_review - full_stars >= 0.5 else 0  # Si hay media estrella
            empty_stars = 5 - full_stars - half_star  # Estrellas vacías

            # Generar la lista de clases de estrellas
            stars = (['fas fa-star'] * full_stars + 
                     ['fas fa-star-half-alt'] * half_star + 
                     ['far fa-star'] * empty_stars)
        else:
            stars = ['far fa-star'] * 5  # Si no tiene reseñas, todas las estrellas estarán vacías

        productos_con_estrellas.append({
            'producto': producto,
            'stars': stars,
            'average_review': average_review,  # Agregamos el promedio para ordenarlo
        })

    # Ordenar los productos por el promedio de reseñas (de mayor a menor)
    productos_con_estrellas = sorted(productos_con_estrellas, key=lambda x: x['average_review'], reverse=True)

    # Tomar solo los primeros 6 productos mejor valorados
    productos_mejor_valorados = productos_con_estrellas[:8]

    context = {
        'productos_con_estrellas': productos_mejor_valorados,
    }
    
    return render(request, 'home.html', context)