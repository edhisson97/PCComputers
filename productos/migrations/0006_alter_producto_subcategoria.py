# Generated by Django 4.2.6 on 2023-11-15 19:27

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0005_marca'),
        ('productos', '0005_alter_producto_subcategoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='subcategoria',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='categoria', chained_model_field='id_categoria', on_delete=django.db.models.deletion.CASCADE, to='inicio.subcategoria'),
        ),
    ]