from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Registro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    fecha_hora = models.DateTimeField()  # Guarda la fecha y hora automáticamente al crear el registro
    total_vendido = models.DecimalField(max_digits=10, decimal_places=2)  # Campo para el total vendido en decimal
    total_descuento = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # Campo para el total de descuento en decimal
    numero_factura = models.CharField(max_length=100,null=True)  # Campo para el número de factura
    vendedor_id = models.IntegerField()  # Campo para el ID del vendedor

    def __str__(self):
        #return f"Registro - {self.numero_factura}"
        return f"Registro (ID: {self.id})"
    

class Factura(models.Model):
    url = models.CharField(max_length=200,null=True)  # Campo para el número de factura
    fecha_emision = models.DateField(auto_now_add=True)
    # otros campos de la factura
    
    def __str__(self):
        return self.numero