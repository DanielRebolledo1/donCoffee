# Generated by Django 5.1.2 on 2024-11-06 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_pedido_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='metodo_envio',
            field=models.CharField(choices=[('domicilio', 'Envío a Domicilio'), ('tienda', 'Retiro en Tienda')], default='domicilio', max_length=10),
        ),
    ]
