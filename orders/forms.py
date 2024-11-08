from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['first_name', 'last_name', 'phone', 'email', 'direccion',
                  'ciudad', 'indicaciones', 'nota_pedido']