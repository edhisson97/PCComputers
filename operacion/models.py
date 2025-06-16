from django.db import models
from django.contrib.auth.models import User
from productos.models import ColorStock, Producto

# Create your models here.
class Proveedor(models.Model):
    ruc = models.CharField(max_length=13, unique=True, verbose_name='RUC')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    ciudad = models.CharField(max_length=200, verbose_name='Ciudad',null=True)
    direccion = models.CharField(max_length=200, verbose_name='Dirección',null=True)
    contacto = models.CharField(max_length=100, verbose_name='Contacto',null=True)
    email = models.EmailField(verbose_name='Email',null=True)
    telefono = models.CharField(max_length=20, verbose_name='Teléfono',null=True)

    def __str__(self):
        return self.nombre
    


class Caja(models.Model):
    cajero = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_hora_inicio = models.DateTimeField(auto_now_add=True)
    valor_apertura = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True,null=True)
    fecha_hora_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='abierta')
    numero_caja = models.CharField(max_length=20, null=True, blank=True)
    efectivo_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efectivo_servicios = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_servicios = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_general = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efectivo_contado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    #def __str__(self):
    #    return f"Caja de {self.cajero.username} - {self.fecha_hora_inicio}"
    
class Gasto(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=20,null=True, blank=True)
    
class Ingreso(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=20,null=True, blank=True)
    
class ActualizacionStock(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True)
    numeroFactura = models.CharField(max_length=20, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    
class ProductosActualizacion(models.Model):
    actualizacionstock = models.ForeignKey(ActualizacionStock, on_delete=models.CASCADE,null=True, blank=True)
    colorstock = models.ForeignKey(ColorStock, on_delete=models.CASCADE,null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE,null=True, blank=True)
    cantidad = models.CharField(max_length=20, null=True)
    precio_actualizado = models.CharField(max_length=10,null=True, blank=True)