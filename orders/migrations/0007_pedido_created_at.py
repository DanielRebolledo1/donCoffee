# Generated by Django 5.1.2 on 2024-11-15 19:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_remove_pedido_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
