# Generated by Django 4.2.6 on 2025-04-12 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operacion', '0015_productosactualizacion_precio_actualizado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualizacionstock',
            name='numeroFactura',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
