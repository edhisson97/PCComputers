# Generated by Django 4.2.6 on 2024-08-13 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0026_servicio_numero_reparacion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicio',
            old_name='abonado',
            new_name='descuento',
        ),
    ]
