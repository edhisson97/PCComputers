# Generated by Django 4.2.6 on 2024-05-03 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0002_alter_registro_fecha_hora'),
    ]

    operations = [
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20, unique=True)),
                ('direccion', models.CharField(max_length=200, null=True)),
            ],
        ),
    ]