from django.db import models
from django.urls import reverse
from django.utils.text import slugify

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
    
    
    def save(self, *args, **kwargs):
        # Genera un slug automáticamente si está vacío
        if not self.slug:
            base_slug = slugify(self.nombre_categoria)
            slug = base_slug
            # Verifica si el slug ya existe
            counter = 1
            while Categoria.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(Categoria, self).save(*args, **kwargs)


    # Manager explícito
    objects = models.Manager()
    
    def __str__(self):
        return str(self.nombre_categoria)