# Generated by Django 4.2.6 on 2024-12-12 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacion', '0009_caja_efectivo_contado_caja_efectivo_servicios_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caja',
            name='total_efectivo',
        ),
    ]
