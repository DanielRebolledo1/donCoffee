# Generated by Django 5.1.2 on 2024-11-06 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_pedido_metodo_envio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='metodo_envio',
        ),
    ]
