from django.contrib import admin
from .models import Proveedor, Caja, Gasto, Ingreso
# Register your models here.
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id','ruc','nombre','ciudad','direccion','contacto','email','telefono','numeroFactura')

@admin.register(Gasto)
class GastosAdmin(admin.ModelAdmin):
    list_display = ('id', 'caja','valor', 'descripcion', 'fecha_hora','usuario')
    
@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('id', 'caja','valor', 'descripcion', 'fecha_hora','usuario')

class CajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cajero', 'fecha_hora_inicio', 'valor_apertura', 'fecha_hora_cierre', 'estado','observaciones','numero_caja')
    list_filter = ('cajero', 'fecha_hora_inicio', 'fecha_hora_cierre', 'estado')
    search_fields = ('cajero__username', 'observaciones')
    readonly_fields = ('fecha_hora_inicio',)

admin.site.register(Caja, CajaAdmin)