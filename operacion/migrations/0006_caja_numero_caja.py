# Generated by Django 4.2.6 on 2024-07-04 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operacion', '0005_gasto_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='caja',
            name='numero_caja',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
