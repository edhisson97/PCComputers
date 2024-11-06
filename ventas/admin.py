from django.contrib import admin
from .models import Registro, Deudas, Pago, FacturaCredito, Servicio, PagoRegistroCombinado, Equipo, DescripcionEquipo

# Register your models here.
@admin.register(Registro)
class registroAdmin(admin.ModelAdmin):
    list_display = ('id','usuario','fecha_hora','numero_factura','vendedor_id','tipo_venta','tipo_pago','deuda','total_vendido','total_descuento','adelanto')
    
@admin.register(PagoRegistroCombinado)
class registroCombinadoAdmin(admin.ModelAdmin):
    list_display = ('id','registro','valorEfectivo','valorTarjetaCredito','valorCheque')

@admin.register(Deudas)
class deudasAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'saldo')

@admin.register(Pago)
class deudasAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'deuda', 'cuota','estado')
    
@admin.register(FacturaCredito)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'fecha', 'total')  # Campos que se mostrarán en la lista de facturas en el admin
    search_fields = ('nombre', 'apellidos', 'numeroFactura')  # Campos que se pueden utilizar para búsqueda en el admin
    list_filter = ('fecha', 'tipoPago', 'tipoVenta') 
    
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_ingreso', 'fecha_entrega', 'equipo', 'marca', 'tecnico_asignado', 'costo', 'saldo','abonado','descripcion_problema')
    list_filter = ('fecha_ingreso', 'fecha_entrega', 'tecnico_asignado')
    search_fields = ('equipo', 'marca', 'tecnico_asignado')
    
@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    
@admin.register(DescripcionEquipo)
class DescripcionEquipoAdmin(admin.ModelAdmin):
    list_display = ('equipo','problema','costo')