# Generated by Django 4.2.6 on 2024-06-06 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0017_facturacredito_deuda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturacredito',
            name='productos',
            field=models.JSONField(),
        ),
    ]
