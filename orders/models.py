from django.db import models
from accounts.models import Account
from store.models import Producto, Variante

# Create your models here.


class Pago(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    pago_id = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=100)
    monto_pagado = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pago_id)

class Pedido(models.Model):
    ESTADO = (
        ('Nuevo', 'Nuevo'),
        ('Aceptado', 'Aceptado'),
        ('Completado', 'Completado'),
        ('Cancelado', 'Cancelado'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, blank=True, null=True)
    num_pedido = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    direccion = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=50)
    indicaciones = models.CharField(max_length=150, blank=True)
    nota_pedido = models.CharField(max_length=150, blank=True)
    total_pedido = models.FloatField()
    subtotal = models.FloatField()
    iva = models.FloatField()
    estado = models.CharField(max_length=10, choices=ESTADO, default='Nuevo')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
   
    def __str__(self):
        return str(self.num_pedido) # pylint: disable=no-member

class Pedido_producto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variantes = models.ManyToManyField(Variante, blank=True)
    cantidad = models.IntegerField()
    precio_producto = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.producto.nombre_producto) # pylint: disable=no-member