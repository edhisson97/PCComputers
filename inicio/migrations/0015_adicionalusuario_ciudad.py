# Generated by Django 4.2.6 on 2024-04-17 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0014_adicionalusuario_direccionenvio'),
    ]

    operations = [
        migrations.AddField(
            model_name='adicionalusuario',
            name='ciudad',
            field=models.CharField(max_length=100, null=True),
        ),
    ]