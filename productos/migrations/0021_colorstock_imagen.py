# Generated by Django 4.2.6 on 2023-12-07 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0020_colorstock_color_producto_peso'),
    ]

    operations = [
        migrations.AddField(
            model_name='colorstock',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos'),
        ),
    ]
