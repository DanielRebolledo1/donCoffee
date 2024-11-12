from django import forms
from .models import Producto, ReviewRating

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'precio', 'imagen', 'stock', 'disponible', 'categoria']
        
        
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        
        # Placeholder vacíos si se necesita
        self.fields['nombre_producto'].widget.attrs['placeholder'] = ''
        self.fields['descripcion'].widget.attrs['placeholder'] = ''
        self.fields['imagen'].widget.attrs['placeholder'] = ''
        self.fields['stock'].widget.attrs['placeholder'] = ''

        # Aplicar clases de Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

         # Cambios específicos para los campos
        # Descripción: tamaño estándar y solo lectura
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['style'] = 'resize: none; max-height: 100px;'  # Tamaño estándar

        # Imagen: campo de subida de archivos
        self.fields['imagen'].widget = forms.ClearableFileInput(attrs={'class': 'form-control-file'})

        # Disponible: campo de tipo checkbox
        self.fields['disponible'].widget.attrs['class'] = 'form-check-input large-checkbox'  # Clase para checkbox
        self.fields['disponible'].widget.attrs['style'] = "margin-left: 20px" 
        
    # def clean_nombre_producto(self):
    #      nombre_producto = self.cleaned_data.get('nombre_producto')
    #      if Producto.objects.filter(nombre_producto=nombre_producto).exists():
    #          raise forms.ValidationError(f'Ya existe un producto con el nombre "{nombre_producto}".')
    #      return nombre_producto
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']