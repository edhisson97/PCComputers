# Generated by Django 4.2.6 on 2024-08-13 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0028_servicio_abonado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicio',
            old_name='descuento',
            new_name='costo_sin_descuento',
        ),
    ]