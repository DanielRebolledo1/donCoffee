# Generated by Django 5.1.2 on 2024-10-23 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_variante_variante_precio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variante',
            name='variante_categoria',
            field=models.CharField(choices=[('tamaño', 'tamaño')], max_length=100),
        ),
    ]
