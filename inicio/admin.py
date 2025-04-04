from django.contrib import admin
from .models import Categoria, subCategoria, Marca, Carrusel, Iva, adicionalUsuario, DescuentoServicio

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')  # Campos que se mostrarán en la lista de categorías en el panel de administración

@admin.register(subCategoria)
class subCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id','id_categoria','nombre')
    
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')  
    
@admin.register(Carrusel)
class CarruselAdmin(admin.ModelAdmin):
    list_display = ('id','imagen')
    
@admin.register(Iva)
class IvaAdmin(admin.ModelAdmin):
    list_display = ('porcentaje',)
    
@admin.register(DescuentoServicio)
class DescuentoSAdmin(admin.ModelAdmin):
    list_display = ('porcentaje',)


@admin.register(adicionalUsuario)
class UsuarioAdicionalAdmin(admin.ModelAdmin):
    list_display = ('id','user','token','cedula','celular','ciudad','direccion','direccionEnvio','deuda')