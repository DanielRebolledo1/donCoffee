from django.contrib import admin
from . models import Pago, Pedido, Pedido_producto

# Register your models here.
class PedidoProductoInline(admin.TabularInline):
    model = Pedido_producto
    extra = 0
    readonly_fields = ('pago', 'user', 'producto', 'variantes', 'cantidad', 'ordered')
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['num_pedido', 'full_name', 'phone', 'email', 'direccion', 'total_pedido', 'estado', 'is_ordered', 'created_at']
    list_filter = ['estado', 'is_ordered']
    search_fields = ['num_pedido', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [PedidoProductoInline]

admin.site.register(Pago)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Pedido_producto)