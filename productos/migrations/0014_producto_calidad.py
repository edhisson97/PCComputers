# Generated by Django 4.2.6 on 2023-11-20 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0013_rename_nombre_producto_modelo'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='calidad',
            field=models.CharField(choices=[('original', 'Original'), ('generico', 'Genérico'), ('sn', 'S/N')], default='sn', max_length=10),
        ),
    ]
