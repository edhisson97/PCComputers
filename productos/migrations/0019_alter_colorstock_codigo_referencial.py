# Generated by Django 4.2.6 on 2023-11-20 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0018_alter_colorstock_codigo_referencial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colorstock',
            name='codigo_referencial',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
