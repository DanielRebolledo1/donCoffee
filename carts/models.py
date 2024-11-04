from django.db import models
from store.models import Producto, Variante
from accounts.models import Account


# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    # Manager explícito
    objects = models.Manager()
    
    def __str__(self):
        return str(self.cart_id)
    
class CartItem (models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variantes = models.ManyToManyField(Variante, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    cantidad = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    
    # Manager explícito
    objects = models.Manager()
    
    
    def sub_total(self):
        return self.producto.precio * self.cantidad # pylint: disable=no-member
    
    def __str__(self):
        return str(self.producto)