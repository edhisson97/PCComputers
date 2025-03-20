from django.contrib import admin
# Register your models here.
from .models import Producto, ImagenProducto, ColorStock

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    
class ColorStockInline(admin.TabularInline):
    model = ColorStock
    fields = ['codigo_referencial' ,'color','codigo_color' ,'stock','imagen']
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('modelo','categoria', 'subcategoria','marca','calidad','precio','oferta', 'precio_oferta','detalle','peso', 'desactivado')
    inlines = [
        ImagenProductoInline,
        ColorStockInline
    ]
    
    