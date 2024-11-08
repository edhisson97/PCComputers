# Generated by Django 4.2.6 on 2024-08-07 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operacion', '0007_alter_caja_cajero'),
        ('ventas', '0021_servicio_caja_alter_servicio_abono_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='caja',
        ),
        migrations.CreateModel(
            name='PagoServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('abono', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipoPago', models.CharField(max_length=50)),
                ('numeroCheque', models.CharField(blank=True, max_length=50, null=True)),
                ('combinados', models.TextField(blank=True, null=True)),
                ('caja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operacion.caja')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.servicio')),
            ],
        ),
    ]
