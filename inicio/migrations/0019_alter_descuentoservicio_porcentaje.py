# Generated by Django 4.2.6 on 2024-07-30 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0018_descuentoservicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='descuentoservicio',
            name='porcentaje',
            field=models.CharField(default='3', max_length=3),
        ),
    ]
