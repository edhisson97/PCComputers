# Generated by Django 4.2.6 on 2024-04-17 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0013_iva'),
    ]

    operations = [
        migrations.AddField(
            model_name='adicionalusuario',
            name='direccionEnvio',
            field=models.CharField(max_length=300, null=True),
        ),
    ]