from django.db import models
from inicio.models import Categoria, subCategoria, Marca
from cloudinary.models import CloudinaryField
from smart_selects.db_fields import GroupedForeignKey

# Create your models here.
class Producto(models.Model):
    OPCIONES_CALIDAD = [
        ('original', 'Original'),
        ('generico', 'Genérico'),
        ('sn', 'S/N'),
    ]
    modelo = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = GroupedForeignKey(subCategoria, "id_categoria",on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    calidad = models.CharField(max_length=10, choices=OPCIONES_CALIDAD, default='sn')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    detalle = models.CharField(max_length=600,null=True, help_text="Detalles precisos que van en la presentación del producto.")
    descripcion = models.TextField(null=True,help_text="Toda la descripción y características del producto.")
    peso = models.DecimalField(default=0.5,max_digits=5,decimal_places=2,help_text="Peso en Kilogramos (Kg)")  
    oferta = models.BooleanField(default=False)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Este campo no es necesario.")
    desactivado = models.CharField(max_length=2, null=True)

    def __str__(self):
        return self.modelo
    
class ImagenProducto(models.Model):
    imagen = CloudinaryField('image', folder='productos')
    # PARA SERVIDORES QUE SOPRTAN ARCHIVOS ESTATICOS
    #imagen = models.ImageField(upload_to="productos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE,related_name="imagenes")
    
class ColorStock(models.Model):
    codigo_referencial = models.CharField(max_length=255,null=True)
    color = models.CharField(max_length=100,null=True)
    codigo_color = models.CharField(max_length=10, default="#050505",help_text="El código del producto debe ser HEX ejemplo:'#050505' o '#fcfcfc'.")
    stock = models.IntegerField(default=1)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="colores")
    imagen = CloudinaryField('image', folder='productos', null=True, blank=True)
    # PARA SERVIDORES QUE SOPRTAN ARCHIVOS ESTATICOS
    #imagen = models.ImageField(upload_to="productos", null=True, blank=True)
    
