from django.contrib import admin
from .models import Producto, Variante, ReviewRating

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'precio', 'stock', 'categoria', 'fecha_creacion', 'fecha_modificacion', 'disponible')
    prepopulated_fields = {'slug':('nombre_producto',)}
    
class VarianteAdmin(admin.ModelAdmin):
    list_display = ('producto', 'variante_categoria','variante_precio', 'variante_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('producto', 'variante_categoria', 'variante_value')

    
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Variante, VarianteAdmin)
admin.site.register(ReviewRating)