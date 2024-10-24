from django.db import models
from django.urls import reverse

# Create your models here.

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    descripcion = models.TextField(max_length = 255, blank=True)
    cat_imagen = models.ImageField(upload_to= 'photos/categories', blank=True)
    
    class meta:
        verbose_name= 'Categoria'
        verbose_name_plural= 'Categorias'
        
    def get_url(self):
        return reverse('productos_por_categoria', args=[self.slug])
    
    # Manager explícito
    objects = models.Manager()
    
    def __str__(self):
        return str(self.nombre_categoria)