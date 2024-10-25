from django.db import models
from category.models import Categoria
from django.urls import reverse

# Create your models here.

class Producto(models.Model):
    nombre_producto = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion = models.TextField(max_length=500, blank=True)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='photos/products') 
    stock = models.IntegerField()
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Manager explícito
    objects = models.Manager()

    def get_url(self):
        return reverse('product_detail', args=[self.categoria.slug, self.slug]) # pylint: disable=no-member

    def __str__(self):
        return str(self.nombre_producto)



class VarianteManager(models.Manager):
    def tamaño(self):
        return super(VarianteManager, self).filter(variante_categoria='tamaño', is_active=True)


variante_categoria_choice = (

    ('tamaño', 'tamaño'),

)

variante_value_choice = (

    # ('Pequeño', 'Pequeño'),
    ('Estandar', 'Estandar'),
    # ('Grande', 'Grande'),

)

class Variante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variante_categoria = models.CharField(max_length=100, choices=variante_categoria_choice)
    variante_precio = models.IntegerField()
    variante_value = models.CharField(max_length=100, choices=variante_value_choice)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now=True)

    objects = VarianteManager()

    def __str__(self):
        return str(self.variante_value)