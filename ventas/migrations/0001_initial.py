# Generated by Django 4.2.6 on 2024-04-23 03:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('total_vendido', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_descuento', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('numero_factura', models.CharField(max_length=100, null=True)),
                ('vendedor_id', models.IntegerField()),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]