# Generated by Django 4.2.6 on 2023-11-15 16:31

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0005_marca'),
        ('productos', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='subcategoria',
            field=smart_selects.db_fields.GroupedForeignKey(group_field='categoria', on_delete=django.db.models.deletion.CASCADE, to='inicio.subcategoria'),
        ),
    ]