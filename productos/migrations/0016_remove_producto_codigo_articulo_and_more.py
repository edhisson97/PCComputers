# Generated by Django 4.2.6 on 2023-11-20 01:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0015_rename_stock_producto_codigo_articulo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='codigo_articulo',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='codigo_referencial',
        ),
        migrations.CreateModel(
            name='ColorStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_articulo', models.IntegerField(default=1)),
                ('codigo_referencial', models.CharField(max_length=255, null=True)),
                ('codigo_color', models.CharField(default='#050505', help_text="El código del producto debe ser HEX ejemplo:'#050505' o '#fcfcfc'.", max_length=10)),
                ('stock', models.IntegerField(default=1)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
            ],
        ),
    ]
