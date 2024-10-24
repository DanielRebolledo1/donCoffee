from django.shortcuts import render
from store.models import Producto

def home(request):
    productos = Producto.objects.all().filter(disponible=True)
    
    context = {
        'productos': productos,
        
    }
    
    return render(request, 'home.html', context)