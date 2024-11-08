from django.contrib import admin
from . models import Pago, Pedido, Pedido_producto

# Register your models here.

admin.site.register(Pago)
admin.site.register(Pedido)
admin.site.register(Pedido_producto)