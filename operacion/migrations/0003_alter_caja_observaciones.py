# Generated by Django 4.2.6 on 2024-06-13 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operacion', '0002_caja'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caja',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
        ),
    ]
