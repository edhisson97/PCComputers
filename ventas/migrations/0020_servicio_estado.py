# Generated by Django 4.2.6 on 2024-07-02 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0019_servicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='estado',
            field=models.CharField(default='pendiente', max_length=10),
        ),
    ]
