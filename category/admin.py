from django.contrib import admin
from .models import Categoria

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    list_display = ('nombre_categoria', 'slug')

admin.site.register(Categoria, CategoryAdmin)