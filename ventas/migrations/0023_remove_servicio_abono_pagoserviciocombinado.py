# Generated by Django 4.2.6 on 2024-08-08 02:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0022_remove_servicio_caja_pagoservicio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='abono',
        ),
        migrations.CreateModel(
            name='PagoServicioCombinado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valorEfectivo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valorTarjeta', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valorCheque', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valorTransferencia', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('pagoServicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.pagoservicio')),
            ],
        ),
    ]