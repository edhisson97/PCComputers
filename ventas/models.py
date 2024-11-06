from django.db import models
from django.contrib.auth.models import User
from operacion.models import Caja

# Create your models here.
class Registro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    fecha_hora = models.DateTimeField()  # Guarda la fecha y hora automáticamente al crear el registro
    total_vendido = models.DecimalField(max_digits=10, decimal_places=2)  # Campo para el total vendido en decimal
    total_descuento = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # Campo para el total de descuento en decimal
    numero_factura = models.CharField(max_length=100,null=True)  # Campo para el número de factura
    vendedor_id = models.IntegerField()  # Campo para el ID del vendedor
    tipo_venta = models.CharField(max_length=100,null=True)
    tipo_pago = models.CharField(max_length=100,null=True)
    deuda = models.CharField(max_length=3, default='no')
    adelanto = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    
    def __str__(self):
        #return f"Registro - {self.numero_factura}"
        return f"Registro (ID: {self.id})"
    
class PagoRegistroCombinado(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    valorEfectivo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaCredito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaDebito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorCheque = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTransferencia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
class Deudas(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    registro = models.ForeignKey(Registro, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    total = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, default='pendiente')#el otro estado es pagada
    
    
    def __str__(self):
        #return f"Registro - {self.numero_factura}"
        return f"Deuda (ID: {self.id})"

class Pago(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    deuda = models.ForeignKey(Deudas, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    fecha_hora = models.DateTimeField()  # Guarda la fecha y hora automáticamente al crear el registro
    cuota = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, default='pendiente')#el otro estado es terminado
    tipoPago = models.CharField(max_length=50, blank=True, null=True)
    numeroCheque = models.CharField(max_length=50, blank=True, null=True)
    banco = models.CharField(max_length=50, blank=True, null=True)
    numeroTransferencia = models.CharField(max_length=50, blank=True, null=True)
    
class PagoPendienteCombinado(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    valorEfectivo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaCredito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaDebito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorCheque = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTransferencia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)



class Factura(models.Model):
    url = models.CharField(max_length=200,null=True)  # Campo para el número de factura
    fecha_emision = models.DateField(auto_now_add=True)
    # otros campos de la factura
    
    def __str__(self):
        return self.numero
    
class FacturaCredito(models.Model):
    deuda = models.ForeignKey(Deudas, on_delete=models.SET_NULL, null=True)  # Relaciona con el modelo User de Django
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20)
    email = models.EmailField()
    celular = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    direccionEnvio = models.CharField(max_length=255)
    productos = models.JSONField()
    subtotal = models.CharField(max_length=20)
    porcentaje = models.CharField(max_length=20)
    descuento = models.CharField(max_length=20)
    subtotalD = models.CharField(max_length=20)
    porcentajeDescuento = models.CharField(max_length=20)
    iva = models.CharField(max_length=20)
    total = models.CharField(max_length=20)
    tipoPago = models.CharField(max_length=50)
    peso = models.CharField(max_length=20)
    fecha = models.CharField(max_length=100)
    numeroCheque = models.CharField(max_length=50, blank=True, null=True)
    numeroFactura = models.CharField(max_length=50)
    combinados = models.TextField(blank=True,null=True)
    tipoVenta = models.CharField(max_length=50)
    abono = models.CharField(max_length=20)
    saldo = models.CharField(max_length=20)
    usuarioVendedor = models.CharField(max_length=100)

    def __str__(self):
        return f"Factura {self.numeroFactura}"
    
class Servicio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    tipo_servicio = models.CharField(max_length=100)
    equipo = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serie = models.CharField(max_length=100)
    descripcion_problema = models.TextField()
    solucion = models.TextField(blank=True, null=True)
    tecnico_asignado = models.CharField(max_length=100)
    usuario_recepta = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    costo_sin_descuento = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    abonado = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    estado = models.CharField(max_length=10, default='pendiente')#el otro estado es terminado
    numero_reparacion = models.IntegerField(blank=True, null=True)  
    
class PagoServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    abono = models.DecimalField(max_digits=10, decimal_places=2)
    tipoPago = models.CharField(max_length=50)
    numeroCheque = models.CharField(max_length=50, blank=True, null=True)
    banco = models.CharField(max_length=50, blank=True, null=True)
    numeroTransferencia = models.CharField(max_length=50, blank=True, null=True)
    
class PagoServicioCombinado(models.Model):
    pagoServicio = models.ForeignKey(PagoServicio, on_delete=models.CASCADE)
    valorEfectivo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaCredito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTarjetaDebito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorCheque = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valorTransferencia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
class Equipo(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.nombre
    
class DescripcionEquipo(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    problema = models.CharField(max_length=70, blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
