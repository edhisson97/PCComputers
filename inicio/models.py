from django.db import models
from django.contrib.auth.models import Group, User
from django.db import models


# Crear grupos
#seller_group, created = Group.objects.get_or_create(name='Vendedores')
#Seller_group, created = Group.objects.get_or_create(name='Operadores')
#Seller_group, created = Group.objects.get_or_create(name='Tecnicos')

class adicionalUsuario(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True, null=True)
    cedula = models.CharField(max_length=10, unique=True, null=True)
    celular = models.CharField(max_length=10, null=True)
    ciudad = models.CharField(max_length=100, null=True)
    direccion = models.CharField(max_length=200, null=True)
    direccionEnvio = models.CharField(max_length=300, null=True)
    deuda = models.CharField(max_length=3, default='no')

    def __str__(self):
        return self.token

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="categorias", null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class subCategoria(models.Model):
    id_categoria = models.ForeignKey(Categoria, null=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="subCategorias", null=True, blank=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    
class Carrusel(models.Model):
    imagen = models.ImageField(upload_to="carrusel")

    def __int__(self):
        return self.id
    
class Iva(models.Model):
    porcentaje = models.CharField(max_length=3)

    def __str__(self):
        return self.porcentaje
    
    @classmethod
    def get_iva(cls):
        # Devuelve el único registro de IVA, creándolo con el valor predeterminado si no existe
        obj, created = cls.objects.get_or_create(id=1, defaults={'porcentaje': '15'})
        return obj

    def save(self, *args, **kwargs):
        # Anula el método save para evitar la creación de nuevos registros
        if self.pk is None:
            self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Anula el método delete para evitar la eliminación del registro
        pass
    
class DescuentoServicio(models.Model):
    porcentaje = models.CharField(max_length=3)

    def __str__(self):
        return self.porcentaje
    
    @classmethod
    def get_descuento_servicio(cls):
        # Devuelve el único registro de IVA, creándolo con el valor predeterminado si no existe
        obj, created = cls.objects.get_or_create(id=1, defaults={'porcentaje': '3'})
        return obj

    def save(self, *args, **kwargs):
        # Anula el método save para evitar la creación de nuevos registros
        if self.pk is None:
            self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Anula el método delete para evitar la eliminación del registro
        pass