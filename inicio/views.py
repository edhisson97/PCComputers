from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Categoria, Carrusel, Marca, adicionalUsuario, Iva
from productos.models import Producto
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
import secrets
from decimal import Decimal


def login_with_google(request):
    return redirect('social:begin', 'google-oauth2')

def ingresar(request):
    mensaje_error = None  # Inicializa el mensaje de error
    
    if request.method == 'POST':
        credencial = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        # Buscar usuario por cédula (username) o correo electrónico
        usuario = User.objects.filter(email=credencial).first()
        if not usuario:
            usuario = User.objects.filter(username=credencial).first()

        if usuario:
            # Autenticar usando username (que almacena la cédula)
            usuario_autenticado = authenticate(request, username=usuario.username, password=contrasena)

            if usuario_autenticado:
                login(request, usuario_autenticado)
                return redirect('/perfil/')  # Redirigir a la página principal después del inicio de sesión
            else:
                mensaje_error = "Cédula/Correo o contraseña incorrectos."
        else:
            mensaje_error = "Usuario no encontrado."

    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "home.html",)
    try:
        carrusel = Carrusel.objects.all()
    except Carrusel.DoesNotExist:
        return render(request, "home.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "home.html",)
    

    return render(request, 'home.html', {'mensaje_error': mensaje_error,"categoria": categoria,"carrusel":carrusel,"todosProductos":todosProductos})

def cerrar_sesion(request):
    logout(request)
    return redirect('/')



def perfil(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "perfil.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "perfil.html",)
    return render(request, 'perfil.html', {"categoria": categoria,"todosProductos":todosProductos})


def registro(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "home.html",)
    try:
        carrusel = Carrusel.objects.all()
    except Carrusel.DoesNotExist:
        return render(request, "home.html",)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        cedula = request.POST.get('cedula')
        celular = request.POST.get('celular')
        direccion = request.POST.get('direccion')
        
        cedula_correcta = validar_cedula_ecuador(cedula)
        
        if cedula_correcta is False:
            mensaje_alerta = "El número de cédula ingresado es incorrecto."
            return render(request, 'home.html', {'mensaje_alerta': mensaje_alerta,"categoria": categoria,"carrusel":carrusel,})
        
        if User.objects.filter(username=correo).exists():
            mensaje_alerta = "El correo electronico ingresado ya se encuentra registrado."
           
            return render(request, 'home.html', {'mensaje_alerta': mensaje_alerta,"categoria": categoria,"carrusel":carrusel,})
        
        
        if adicionalUsuario.objects.filter(cedula=cedula).exists():
            usuario_adicional = adicionalUsuario.objects.get(cedula=cedula)# luego debo comprobar si el user es active
            usuario = usuario_adicional.user
            print("1111111111111111")
            if usuario and usuario.is_active:
                print("222222222222222222222")
                mensaje_alerta = "El número de cédula ingresado ya se encuentra registrado."
                return render(request, 'home.html', {'mensaje_alerta': mensaje_alerta,"categoria": categoria,"carrusel":carrusel,})
            
            else: #cuando un usuario se encuentra en la bd pero no tiene cuenta en pagina
                print("333333333333333333333333")
                # Actualizar los campos del usuario con los nuevos valores
                usuario.first_name = nombre
                usuario.last_name = apellido
                usuario.email = correo
                usuario.username = correo
                usuario.set_password(contrasena)

                # Guardar los cambios en el usuario
                usuario.save()
                
                token = generar_token_unico()
            
                # Enviar el correo de verificación
                subject = 'Verificación de correo electrónico'
                html_message = render_to_string('correo_verificacion.html', {'usuario': usuario,'token':token})
                plain_message = strip_tags(html_message)
                from_email = 'noreply@example.com'
                to_email = usuario.email

                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
                
                try:
                    u = User.objects.get(email=correo)
                    # El usuario fue encontrado
                    print(usuario)
                except User.DoesNotExist:
                    print('no encontrado')
                    
                usuario_adicional.direccion = direccion
                usuario_adicional.celular = celular
                usuario_adicional.token = token
                usuario_adicional.save()
                # Imprimir los valores del usuario después de crearlo y guardarlos
                print("ID de usuario:", usuario.id)
                print("Nombre de usuario:", usuario.username)
                print("Correo electrónico:", usuario.email)
                print("Nombre:", usuario.first_name)
                print("Apellido:", usuario.last_name)
                print("contra:", usuario.password)
                print("¿Está activo?:", usuario.is_active)
                
                return render(request, 'verificar_correo.html', {"categoria": categoria,})
            
        else:
            print("44444444444444444444444444")
            # Crear un nuevo usuario
            usuario = User.objects.create_user(username=cedula, email=correo, password=contrasena)
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.is_active = False
            usuario.save()

            token = generar_token_unico()
            
            # Enviar el correo de verificación
            subject = 'Verificación de correo electrónico'
            html_message = render_to_string('correo_verificacion.html', {'usuario': usuario,'token':token})
            plain_message = strip_tags(html_message)
            from_email = 'noreply@example.com'
            to_email = usuario.email

            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            
            try:
                u = User.objects.get(email=correo)
                # El usuario fue encontrado
                print(usuario)
            except User.DoesNotExist:
                print('no encontrado')
            
            adicionalU = adicionalUsuario()
            adicionalU.token = token
            adicionalU.user = u
            adicionalU.cedula = cedula
            adicionalU.celular = celular
            adicionalU.direccion = direccion
            adicionalU.save()
    
    return render(request, 'verificar_correo.html', {"categoria": categoria,})

def generar_token_unico():
    return secrets.token_urlsafe(30)

def validar_cedula_ecuador(cedula):
    if len(cedula) != 10:
        return False  # La longitud de la cédula debe ser 10
    try:
        int(cedula)  # Verificar que la cédula sea un número
    except ValueError:
        return False
    
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False  # Los dos primeros dígitos representan la provincia, deben estar entre 1 y 24

    tercer_digito = int(cedula[2])
    if tercer_digito < 0 or tercer_digito > 5:
        return False  # El tercer dígito puede ser 0, 1, 2, 3, 4 o 5

    total = 0
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor > 9:
            valor -= 9
        total += valor

    digito_verificador = (total // 10 + 1) * 10 - total
    if digito_verificador == 10:
        digito_verificador = 0
    
    if digito_verificador == int(cedula[9]):
        return True
    else:
        return False

def verificar_correo(request, token):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "verificacion_exitosa.html",)
    # Buscar el objeto adicionalUsuario con el token proporcionado
    usuario_adicional = get_object_or_404(adicionalUsuario, token=token)

    # Acceder al usuario asociado a través de la relación OneToOne
    usuario = usuario_adicional.user

    # Realizar la verificación del correo electrónico
    usuario.is_active = True
    
    usuario.save()

    # Puedes eliminar el objeto adicionalUsuario si lo deseas
    #usuario_adicional.delete()
    
    mensaje = 'Tu correo electrónico ha sido verificado correctamente. Ahora puedes '
    
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "verificacion_exitosa.html",)

    return render(request, 'verificacion_exitosa.html', {"categoria": categoria, "mensaje":mensaje,"todosProductos":todosProductos})

# Create your views here.
def pagina_inicio(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "home.html",)
    try:
        carrusel = Carrusel.objects.all()
    except Carrusel.DoesNotExist:
        return render(request, "home.html",)
    try:
        productos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "home.html",)
    return render(request, "paginainicio.html", {"categoria": categoria,"carrusel":carrusel,"todosProductos":productos})

def pagina_inicio(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "home.html",)
    try:
        carrusel = Carrusel.objects.all()
    except Carrusel.DoesNotExist:
        return render(request, "home.html",)
    try:
        productos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "home.html",)
    return render(request, "home.html", {"categoria": categoria,"carrusel":carrusel,"todosProductos":productos} )

def pagina_ofertas(request):
    option_value = request.GET.get('option', None)
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "ofertas.html",)
    try:
        if (option_value == "MenorPrecio"):
            productos = Producto.objects.filter(oferta = True).exclude(desactivado="si").order_by('precio_oferta').distinct()
        elif (option_value == "MayorPrecio"):
            productos = Producto.objects.filter(oferta = True).exclude(desactivado="si").order_by('-precio_oferta').distinct()
        else:
            productos = Producto.objects.filter(oferta = True).exclude(desactivado="si").distinct()
    except Producto.DoesNotExist:
        return render(request, "ofertas.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "ofertas.html",)
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
    return render(request, "ofertas.html", {"productos":productos,"categoria": categoria,"todosProductos":todosProductos} )


#para el carrito 
def obtener_carrito(request):
    # Obtiene la cadena JSON de los productos del carrito desde la solicitud GET
    productos_carrito_json = request.GET.get('storedProducts', '[]')

    # Convierte la cadena JSON en una lista de productos
    productos_carrito = json.loads(productos_carrito_json)
    

    
    #valor a cancelar de los produccto
    subtotal = 0
    
    #para el iva
    try:
        iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
        porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
    except Iva.DoesNotExist:
        # Maneja la situación donde el objeto Iva no existe en la base de datos
        porcentaje_iva = 0
    
     # Obtiene los objetos Producto de la base de datos usando los IDs del carrito
    productos_en_carrito = []

    for producto_id in productos_carrito:
        # Utiliza get_object_or_404 para obtener el Producto por ID
        producto = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=producto_id)
        
        #marca = get_object_or_404(Marca, id=producto.marca)
        
        # Obtiene la primera imagen asociada al producto (si existe)
        primera_imagen = producto.imagenes.first()
        
        # Obtener todos los colores y stocks asociados al producto
        colores_y_stock = producto.colores.all()
        
        # Lista para almacenar la información sobre colores y stock
        lista_colores_stock = []

       
        # Recorrer todos los colores y stocks asociados
        for color_stock in colores_y_stock:
            codigo_color = color_stock.codigo_color
            stock = color_stock.stock

            # Agregar información a la lista
            lista_colores_stock.append({
                'codigo_color': codigo_color,
                'stock': stock,
            })
            
        #iva del producto en cuestion
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
        
        #reviso si producto tiene oferta
        if (producto.precio_oferta):
            subtotal = subtotal + producto.precio_oferta
        else:
            subtotal = subtotal + producto.precio
        
        productos_en_carrito.append({
            'id': producto.id,
            'modelo': producto.modelo,
            'marca': producto.marca,
            'precio': producto.precio,
            'precio_oferta': producto.precio_oferta,
            'detalle': producto.detalle,
            'imagen': primera_imagen.imagen.url if primera_imagen else None,
            'colores_stock': lista_colores_stock,
            # Agrega otros campos que necesites
        })
    
    # Renderiza la barra lateral del carrito con los productos
    return render(request, 'barra_lateral_carrito.html', {'productos_en_carrito': productos_en_carrito, "subtotal":subtotal,})

def carrito(request):
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "carrito.html",)
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "carrito.html",)
    
    # Obtiene la cadena JSON de los productos del carrito desde la solicitud GET
    productos_carrito_json = request.GET.get('storedProducts', '[]')

    # Convierte la cadena JSON en una lista de productos
    productos_carrito = json.loads(productos_carrito_json)
    

    
    #valor a cancelar de los produccto
    subtotal = 0
    totalp = 0
    
    #para el iva
    try:
        iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
        porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
    except Iva.DoesNotExist:
        # Maneja la situación donde el objeto Iva no existe en la base de datos
        porcentaje_iva = 0
    
     # Obtiene los objetos Producto de la base de datos usando los IDs del carrito
    productos_en_carrito = []

    for producto_id in productos_carrito:
        # Utiliza get_object_or_404 para obtener el Producto por ID
        producto = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=producto_id)
        
        #marca = get_object_or_404(Marca, id=producto.marca)
        
        # Obtiene la primera imagen asociada al producto (si existe)
        primera_imagen = producto.imagenes.first()
        
        # Obtener todos los colores y stocks asociados al producto
        colores_y_stock = producto.colores.all()
        
        # Lista para almacenar la información sobre colores y stock
        lista_colores_stock = []

       
        # Recorrer todos los colores y stocks asociados
        for color_stock in colores_y_stock:
            codigo_color = color_stock.codigo_color
            stock = color_stock.stock
            color = color_stock.color

            # Agregar información a la lista
            lista_colores_stock.append({
                'codigo_color': codigo_color,
                'stock': stock,
                'color':color,
            })
            
        #iva del producto en cuestion
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
        
        #reviso si producto tiene oferta
        if (producto.precio_oferta):
            subtotal = subtotal + producto.precio_oferta
        else:
            subtotal = subtotal + producto.precio
        
        totalp = totalp + 1
        
        productos_en_carrito.append({
            'id': producto.id,
            'modelo': producto.modelo,
            'marca': producto.marca,
            'precio': producto.precio,
            'precio_oferta': producto.precio_oferta,
            'detalle': producto.detalle,
            'imagen': primera_imagen.imagen.url if primera_imagen else None,
            'colores_stock': lista_colores_stock,
            # Agrega otros campos que necesites
        })
        
        
        
    # Renderiza la barra lateral del carrito con los productos
    return render(request, 'carrito.html', {'productos_en_carrito': productos_en_carrito, 'subtotal':subtotal, "totalp":totalp, "categoria":categoria,"todosProductos":todosProductos})

def ventas_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir a alguna página de éxito después del inicio de sesión
            return redirect('/ventas/')
        else:
            # Mostrar un mensaje de error o redirigir a la misma página de inicio de sesión con un mensaje de error
            return render(request, 'ventas_sesion.html', {'error_message': 'Credenciales de acceso inválidas'})
    else:
        return render(request, 'ventas_sesion.html', )
    
def operacion_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir a alguna página de éxito después del inicio de sesión
            return redirect('/operacion/')
        else:
            # Mostrar un mensaje de error o redirigir a la misma página de inicio de sesión con un mensaje de error
            return render(request, 'operacion_sesion.html', {'error_message': 'Credenciales de acceso inválidas'})
    else:
        return render(request, 'operacion_sesion.html', )