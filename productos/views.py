from django.shortcuts import render
from django.http import Http404, HttpResponse
from inicio.models import subCategoria, Categoria, Marca, Iva
from productos.models import Producto
import json
from random import sample
from decimal import Decimal

# Create your views here.
def pagina_productos(request, id):
    try:
        categoria = Categoria.objects.get(id=id)
        #print(subCategoria)
    except Categoria.DoesNotExist:
        raise Http404
    try:
        todosProductos = Producto.objects.all()
    except Producto.DoesNotExist:
        return render(request, "productos.html",)
    try:
        subcategoria = subCategoria.objects.filter(id_categoria = categoria).distinct()
    except subCategoria.DoesNotExist:
        return render(request, "productos.html",)
    try:
        c = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "productos.html",)
    try:
        marcas = Marca.objects.all()
    except Marca.DoesNotExist:
        return render(request, "productos.html",)
    try:
        opcion_seleccionada = request.GET.get('opcion')
        subcategoria_id = request.GET.get('subcategoria_id')
        marca_seleccionada = request.GET.get('marca')
        elimina_localstorage = False
        #tengo que convertir el null de categoria en vacio
        if (subcategoria_id == 'null'):
            subcategoria_id =''
        if (opcion_seleccionada == 'null'):
            opcion_seleccionada =''
        if (marca_seleccionada == 'null'):
            marca_seleccionada =''
        
        
       
        #para subcategoria y demas
        if (subcategoria_id):
            if (opcion_seleccionada):
                if opcion_seleccionada == 'MenorPrecio':
                    if(marca_seleccionada):
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id, marca = marca_seleccionada).order_by('precio').distinct()
                        
                    else:
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).order_by('precio').distinct()
                        
                    pass
                elif opcion_seleccionada == 'MayorPrecio':
                    if(marca_seleccionada):
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id,marca = marca_seleccionada).order_by('-precio').distinct()
                    else:
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).order_by('-precio').distinct()
                    pass
                elif opcion_seleccionada == 'Todo':
                    productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).distinct()
                    pass
                else:
                    if(marca_seleccionada):
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id, oferta = True, marca = marca_seleccionada).distinct()
                    else:
                        productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id, oferta = True).distinct()
                    pass
            elif (marca_seleccionada):
                productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id ,marca = marca_seleccionada).distinct()
            else:
                productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).distinct()
                #elimina_localstorage = True#ojo puede dar problema con el filtrado ****cada que se presiona en subcategoria se reinicia las variables locales de navegador
                
        #para mayor menor precio y demas
        elif (opcion_seleccionada):
            if (subcategoria_id):
                if opcion_seleccionada == 'MenorPrecio':
                    productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).order_by('precio').distinct()
                    pass
                elif opcion_seleccionada == 'MayorPrecio':
                    productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).order_by('-precio').distinct()
                    pass
                elif opcion_seleccionada == 'Todo':
                    productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id).distinct()
                    pass
                else:
                    productos = Producto.objects.filter(categoria = id, subcategoria = subcategoria_id, oferta = True).distinct()
                    pass
            elif (marca_seleccionada):
                if opcion_seleccionada == 'MenorPrecio':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).order_by('precio').distinct()
                    pass
                elif opcion_seleccionada == 'MayorPrecio':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).order_by('-precio').distinct()
                    pass
                elif opcion_seleccionada == 'Todo':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).distinct()
                    pass
                else:
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada, oferta = True).distinct()
                    pass
            else:
                if opcion_seleccionada == 'MenorPrecio':
                    productos = Producto.objects.filter(categoria = id).order_by('precio').distinct()
                    pass
                elif opcion_seleccionada == 'MayorPrecio':
                    productos = Producto.objects.filter(categoria = id).order_by('-precio').distinct()
                    pass
                elif opcion_seleccionada == 'Todo':
                    productos = Producto.objects.filter(categoria = id).distinct()
                    pass
                else:
                    productos = Producto.objects.filter(categoria = id, oferta = True).distinct()
                    pass
        #para marcas y demas
        elif (marca_seleccionada):
            if (opcion_seleccionada):
                if opcion_seleccionada == 'MenorPrecio':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).order_by('precio').distinct()
                    pass
                elif opcion_seleccionada == 'MayorPrecio':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).order_by('-precio').distinct()
                    pass
                elif opcion_seleccionada == 'Todo':
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).distinct()
                    pass
                else:
                    productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada, oferta = True).distinct()
                    pass
            else:
                productos = Producto.objects.filter(categoria = id, marca = marca_seleccionada).distinct()
        #para solo productos sin ningun filtro ******Todos*****
        else:
            productos = Producto.objects.filter(categoria = id).distinct()
            elimina_localstorage = True#ojo puede dar problema con el filtrado de marcas y precios
        #fin del filtrado 
    
        #para el iva
        try:
            iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
            porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
        except Iva.DoesNotExist:
            # Maneja la situación donde el objeto Iva no existe en la base de datos
            porcentaje_iva = 0
        for producto in productos:
            if (producto.precio_oferta):
                precio_con_iva = Decimal(producto.precio_oferta) * (1 + porcentaje_iva)
                # Agrega el precio con IVA al objeto producto
                precio_con_iva = round(precio_con_iva, 2)
                producto.precio_oferta = precio_con_iva
                
            if (producto.precio):
                precio_con_iva = Decimal(producto.precio) * (1 + porcentaje_iva)
                # Agrega el precio con IVA al objeto producto
                precio_con_iva = round(precio_con_iva, 2)
                producto.precio = precio_con_iva
    
    
    except Producto.DoesNotExist:
        return render(request, "productos.html",{"subcategoria":subcategoria,"categoria":c,"categoria_actual":categoria.id,"todosProductos":todosProductos})
    return render(request, "productos.html",{"subcategoria":subcategoria,"categoria":c, "marca":marcas, "productos":productos,"categoria_actual":categoria.id,"elimina_localstorage":elimina_localstorage,"todosProductos":todosProductos,})

def articulo(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "perfil.html",)
    
    try:
        productos = Producto.objects.all()
    except Producto.DoesNotExist:
        return render(request, 'articulo.html', {"categoria": categoria,})
    
    id_articulo = request.GET.get('id')
    
    try:
        marcas = Marca.objects.all()
    except Marca.DoesNotExist:
        return render(request, 'articulo.html', {"categoria": categoria,})
    
    try:
        producto = Producto.objects.get(id=id_articulo)
        
    except Producto.DoesNotExist:
        return render(request, 'articulo.html', {"categoria": categoria,"productos":productos,"marca":marcas})
    
    try:
        ca = Categoria.objects.get(nombre=producto.categoria)
    except Categoria.DoesNotExist:
        raise Http404
    
    try:
        productosSugeridos = Producto.objects.filter(categoria=producto.categoria).exclude(id=producto.id)
        
        
        # Limita a 3 productos aleatorios (asegúrate de que haya al menos 3 productos en la categoría)
        if productosSugeridos.count() >= 3:
            productos_sugeridos_aleatorios = sample(list(productosSugeridos), 3)
        else:
            # Manejar el caso donde hay menos de 3 productos en la categoría
            productosAux =Producto.objects.all().exclude(id=producto.id)
            productosSugeridos = productosAux
            productos_sugeridos_aleatorios = sample(list(productosSugeridos), 3)
        
    except Producto.DoesNotExist:
        return render(request, 'articulo.html', {"categoria": categoria,"productos":productos,"marca":marcas})
    
    #para el iva
    try:
        iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
        porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
    except Iva.DoesNotExist:
        # Maneja la situación donde el objeto Iva no existe en la base de datos
        porcentaje_iva = 0
    #iva del producto buscado en cuestion
    if (producto.precio_oferta):
            precio_con_iva = Decimal(producto.precio_oferta) * (1 + porcentaje_iva)
            # Agrega el precio con IVA al objeto producto
            precio_con_iva = round(precio_con_iva, 2)
            producto.precio_oferta = precio_con_iva
            
    if (producto.precio):
        precio_con_iva = Decimal(producto.precio) * (1 + porcentaje_iva)
        # Agrega el precio con IVA al objeto producto
        precio_con_iva = round(precio_con_iva, 2)
        producto.precio = precio_con_iva
    #iva de los productos sugeridos
    for prod in productosSugeridos:
        if (prod.precio_oferta):
            precio_con_iva = Decimal(prod.precio_oferta) * (1 + porcentaje_iva)
            # Agrega el precio con IVA al objeto producto
            precio_con_iva = round(precio_con_iva, 2)
            prod.precio_oferta = precio_con_iva
            
        if (prod.precio):
            precio_con_iva = Decimal(prod.precio) * (1 + porcentaje_iva)
            # Agrega el precio con IVA al objeto producto
            precio_con_iva = round(precio_con_iva, 2)
            prod.precio = precio_con_iva
    
    return render(request, 'articulo.html', {"categoria": categoria,"prod":producto, "todosProductos":productos, "productosSugeridos":productos_sugeridos_aleatorios,"marca":marcas,"categoria_actual":ca.id,"categoria_nombre":ca.nombre})