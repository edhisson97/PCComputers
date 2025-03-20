from django.shortcuts import render
from inicio.models import Categoria
from productos.models import Producto

# Create your views here.
def contactanos(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "contactanos.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "contactanos.html",)
    return render(request, 'contactanos.html', {"categoria": categoria,"todosProductos":todosProductos})

def servicios(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "servicios.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "servicios.html",)
    return render(request, 'servicios.html', {"categoria": categoria,"todosProductos":todosProductos})

def desarrollo_web(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "desarrolloWeb.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "desarrolloWeb.html",)
    return render(request, 'desarrolloWeb.html', {"categoria": categoria,"todosProductos":todosProductos})

def mantenimiento(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "mantenimiento.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "mantenimiento.html",)
    return render(request, 'mantenimiento.html', {"categoria": categoria,"todosProductos":todosProductos})