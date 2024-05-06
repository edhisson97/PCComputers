from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ventas.decorators import vendedor_required
from django.contrib.auth.models import User
from inicio.models import adicionalUsuario, Iva
from productos.models import Producto, ColorStock
from .models import Registro, Factura
import json
from django.http import JsonResponse
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from datetime import date, datetime, timedelta



import pdfkit
import tempfile
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError


@vendedor_required
def inicio_ventas(request):
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        usuarios = adicionalUsuario.objects.select_related('user').all()
    except adicionalUsuario.DoesNotExist:
        return render(request, "ventas_inicio.html")
    
    # Crear una lista para almacenar los datos combinados de usuarios y sus datos adicionales
    usuarios_con_datos_adicionales = []

    for usuario_adicional in usuarios:
        usuario = usuario_adicional.user
        if usuario:  # Verificar si el usuario existe
            datos_adicionales = {
                'username': usuario.username,
                'nombre': usuario.first_name,
                'apellidos': usuario.last_name,
                'email': usuario.email,
                'cedula': usuario_adicional.cedula,
                'celular': usuario_adicional.celular,
                'ciudad':usuario_adicional.ciudad,
                'direccion': usuario_adicional.direccion,
                'direccionEnvio':usuario_adicional.direccionEnvio,
                # Agrega más campos de ser necesario
            }
            usuarios_con_datos_adicionales.append(datos_adicionales)
            
    # Convertir la lista de diccionarios a una cadena JSON
    usuarios_json = json.dumps(usuarios_con_datos_adicionales)
    
    try:
       todosProductos = Producto.objects.prefetch_related('colores').all()
    except Producto.DoesNotExist:
        return render(request, "ventas_inicio.html",)
    
    #para el iva
    try:
        iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
        porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
    except Iva.DoesNotExist:
        # Maneja la situación donde el objeto Iva no existe en la base de datos
        porcentaje_iva = 0
    for producto in todosProductos:
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

    return render(request, 'ventas_inicio.html', {"usuarios":usuarios_json, "todosProductos":todosProductos})

@vendedor_required
def transacciones_ventas(request):
    option_value = request.GET.get('option', None)
    if (option_value == 'todo'):
        registros = Registro.objects.all().order_by('-id')
        transacciones = 0
        transacciones = registros.count()
        total = 0
        for r in registros:
            total = total + r.total_vendido
        return render(request, 'ventas_operador.html', {"registros":registros,"total":total, "transacciones":transacciones,"option":option_value})
    elif(option_value == 'hoy'):
        registros = Registro.objects.filter(fecha_hora__date=date.today()).order_by('-id')
        transacciones = 0
        transacciones = registros.count()
        total = 0
        for r in registros:
            total = total + r.total_vendido
        return render(request, 'ventas_operador.html', {"registros":registros,"total":total, "transacciones":transacciones,"option":option_value})
    elif(option_value == 'semana'):
        # Obtener la fecha de inicio de la semana (lunes)
        hoy = datetime.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())

        # Obtener la fecha de fin de la semana (domingo)
        fin_semana = inicio_semana + timedelta(days=6)

        # Filtrar los registros por el rango de fechas de la semana
        registros = Registro.objects.filter(fecha_hora__date__range=[inicio_semana, fin_semana]).order_by('-id')
        transacciones = 0
        transacciones = registros.count()
        total = 0
        for r in registros:
            total = total + r.total_vendido
        return render(request, 'ventas_operador.html', {"registros":registros,"total":total, "transacciones":transacciones,"option":option_value})
    elif(option_value == 'mes'):
        # Obtener el primer día del mes actual
        primer_dia_mes = datetime.now().replace(day=1)

        # Obtener el último día del mes actual
        ultimo_dia_mes = primer_dia_mes.replace(day=1, month=primer_dia_mes.month+1) - timedelta(days=1)

        # Filtrar los registros por el rango de fechas del mes actual
        registros = Registro.objects.filter(fecha_hora__date__range=[primer_dia_mes, ultimo_dia_mes]).order_by('-id')
        transacciones = 0
        transacciones = registros.count()
        total = 0
        for r in registros:
            total = total + r.total_vendido
        return render(request, 'ventas_operador.html', {"registros":registros,"total":total, "transacciones":transacciones,"option":option_value})    
    else:
        registros = Registro.objects.all().order_by('-id')[:10]
        registrosTodos = Registro.objects.all()
        transacciones = 0
        transacciones = registrosTodos.count()
        total = 0
        for r in registrosTodos:
            total = total + r.total_vendido
        return render(request, 'ventas_operador.html', {"registros":registros,"total":total, "transacciones":transacciones})

@login_required
@vendedor_required
def productos_facturar(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Obtén los datos del cuerpo de la solicitud
        productos_facturacion = data.get('productosFacturacion', None)  # Obtiene los productos
        descuento = data.get('descuento', None)  # Obtiene 
        

        subtotal = 0
        peso = 0
        productos_a_facturar = []
        
        if productos_facturacion:
            # Procesa los productos como desees
            for producto in productos_facturacion:
                id_producto = producto.get('id')
                codigo = producto.get('codigo')
                color = producto.get('color')
                cantidad = producto.get('cantidad')
                cantidad_decimal = Decimal(str(cantidad))
          
                try:
                    producto_bd = Producto.objects.get(id=id_producto)
                    # Realiza las operaciones necesarias con el producto obtenido
                except Producto.DoesNotExist:
                    return JsonResponse({'error': 'Datos no encontrados'}, )
                #reviso si producto tiene oferta
                if (producto_bd.precio_oferta):
                    precio = producto_bd.precio_oferta
                    preciot = producto_bd.precio_oferta * cantidad_decimal
                else:
                    precio = producto_bd.precio
                    preciot = producto_bd.precio * cantidad_decimal
                #para el peso
                pesop = producto_bd.peso * cantidad_decimal
                peso = peso + pesop
                #para el subtotal
                subtotal = subtotal + preciot
                productos_a_facturar.append({
                    'id': producto_bd.id,
                    'modelo': producto_bd.modelo,
                    #'marca': marca_info,
                    'color':color,
                    'codigo':codigo,
                    'cantidad':cantidad,
                    'precio': precio,
                    'precio_oferta': producto_bd.precio_oferta,
                    'detalle': producto_bd.detalle,
                    'preciot':preciot
                    # Agrega otros campos que necesites
                })
                
            #para descuentos
            if descuento is not None and descuento.strip() != "":
                descuento = float(descuento)
                if(descuento>0):
                    porcentajeDescuento = Decimal(descuento) / Decimal('100')
                    totalDescuento = subtotal * porcentajeDescuento
                    totalDescuento = round(totalDescuento,2)
                    subtotalD = subtotal - totalDescuento
                    
                else:
                    totalDescuento = 0.00
                    descuento = 0
                    subtotalD = subtotal
            else:
                totalDescuento = 0.00
                descuento = 0
                subtotalD = subtotal     
            
            
                
            #para el iva
            try:
                iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
                porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
            except Iva.DoesNotExist:
                # Maneja la situación donde el objeto Iva no existe en la base de datos
                porcentaje_iva = 0
            ivaTotal = subtotalD * porcentaje_iva
            ivaTotal = round(ivaTotal,2)
            totalp = ivaTotal + subtotal
            totalp = round(totalp,2)
               
            
            # Devuelve una respuesta exitosa
            return JsonResponse({'productos': productos_a_facturar,'subtotal':subtotal,'porcentaje':iva.porcentaje, 'iva':ivaTotal, 'total':totalp, 'descuento':totalDescuento,'porcentajeDescuento':descuento,'subtotalD':subtotalD,'peso':peso})
        else:
            # Si no se proporcionaron datos adecuados, devuelve un error
            return JsonResponse({'error': 'Datos no proporcionados correctamente 1'}, status=400)
    else:
        # Si la solicitud no es de tipo POST, devuelve un error
        return JsonResponse({'error': 'Método no permitido 2'}, status=405)

def reciboPago(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        tipoPago = request.POST.get('tipoPago')
        numeroCheque = request.POST.get('numeroCheque')
        cedula = request.POST.get('cedula')
        celular = request.POST.get('celular')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        ciudad = request.POST.get('ciudad')
        direccion = request.POST.get('direccion')
        direccionEnvio = request.POST.get('direccionEnvio')
        email = request.POST.get('email')
        descuento = request.POST.get('descuento')

        # Obtener los datos del localStorage
        productos_facturacion = request.POST.get('productos_facturacion')

        # Realizar el procesamiento necesario con los datos
        subtotal = 0
        totalp = 0
        peso = 0
        productos_fac = []
        
        # Verificar si hay datos en el localStorage
        if productos_facturacion:
            # Analizar la cadena JSON para obtener la lista de productos
            productos_a_facturar = json.loads(productos_facturacion)

            # Realizar el procesamiento necesario con los datos
            subtotal = 0
            totalp = 0
            for producto in productos_a_facturar:
                # Aquí puedes acceder a cada atributo del producto
                id_producto = producto['id']
                colorCompleto = producto['color']
                color = colorCompleto.split('(')[0].strip() # Divide la cadena en dos partes y toma la primera parte (el color)
                codigo = producto['codigo']
                cantidad = producto['cantidad']
                cantidad_decimal = Decimal(str(cantidad))
                
                try:
                    producto_bd = Producto.objects.get(id=id_producto)
                    # Realiza las operaciones necesarias con el producto obtenido
                except Producto.DoesNotExist:
                    return JsonResponse({'error': 'Datos no encontrados'}, )
                #reviso si producto tiene oferta
                if (producto_bd.precio_oferta):
                    precio = producto_bd.precio_oferta
                    preciot = producto_bd.precio_oferta * cantidad_decimal
                else:
                    precio = producto_bd.precio
                    preciot = producto_bd.precio * cantidad_decimal
                #para el peso
                pesop = producto_bd.peso * cantidad_decimal
                peso = peso + pesop
                #para el subtotal
                subtotal = subtotal + preciot
                productos_fac.append({
                    'id': producto_bd.id,
                    'modelo': producto_bd.modelo,
                    'codigo':codigo,
                    #'marca': marca_info,
                    'color':color,
                    'cantidad':cantidad,
                    'precio': precio,
                    'detalle': producto_bd.detalle,
                    'preciot':preciot
                    # Agrega otros campos que necesites
                })
        
        #para descuentos
            if descuento is not None and descuento.strip() != "":
                descuento = float(descuento)
                if(descuento>0):
                    porcentajeDescuento = Decimal(descuento) / Decimal('100')
                    totalDescuento = subtotal * porcentajeDescuento
                    totalDescuento = round(totalDescuento,2)
                    subtotalD = subtotal - totalDescuento
                    
                else:
                    totalDescuento = 0.00
                    descuento = 0
                    subtotalD = subtotal
            else:
                totalDescuento = 0.00
                descuento = 0
                subtotalD = subtotal     
            
            
                
            #para el iva
            try:
                iva = Iva.objects.get(pk=1)  # Suponiendo que el IVA único tiene un ID de 1
                porcentaje_iva = Decimal(iva.porcentaje) / Decimal('100')  # Convertir el porcentaje de IVA a Decimal
            except Iva.DoesNotExist:
                # Maneja la situación donde el objeto Iva no existe en la base de datos
                porcentaje_iva = 0
            ivaTotal = subtotalD * porcentaje_iva
            ivaTotal = round(ivaTotal,2)
            totalp = ivaTotal + subtotal
            totalp = round(totalp,2)
             
        context = {
            'nombre':nombre,
            'apellidos':apellidos,
            'cedula':cedula,
            'email':email,
            'celular':celular,
            'ciudad':ciudad,
            'direccion':direccion,
            'direccionEnvio':direccionEnvio,
            'productos': productos_fac,
            'subtotal':subtotal,
            'porcentaje':iva.porcentaje,
            'iva':ivaTotal, 
            'total':totalp,
            'descuento':totalDescuento,
            'porcentajeDescuento':descuento,
            'subtotalD':subtotalD,
            'tipoPago':tipoPago,
            'peso':peso,
            'numeroCheque':numeroCheque
        }
        
        return render(request, 'reciboPago.html', context)
          
    else:
        # Si no es una solicitud POST, retornar una respuesta de error
        return HttpResponse("Error: Esta vista solo acepta solicitudes POST.")  
    
    
def generarPdf(request):
    if request.method == 'POST':
        if 'confirmar_venta' in request.POST:
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            cedula = request.POST.get('cedula')
            email = request.POST.get('email')
            celular = request.POST.get('celular')
            ciudad = request.POST.get('ciudad')
            direccion = request.POST.get('direccion')
            direccionEnvio = request.POST.get('direccionEnvio')
            subtotal = request.POST.get('subtotal')
            porcentaje = request.POST.get('porcentaje')
            descuento = request.POST.get('descuento')
            subtotalD = request.POST.get('subtotalD')
            porcentajeDescuento = request.POST.get('porcentajeDescuento')
            iva = request.POST.get('iva')
            total = request.POST.get('total')
            tipoPago = request.POST.get('tipoPago')
            peso = request.POST.get('peso')
            numeroCheque = request.POST.get('numeroCheque')
            # Aquí puedes utilizar los datos como necesites
            # Realiza las acciones correspondientes
            
         # Convertir productos de cadena a lista de diccionarios
        # Convertir la cadena JSON de productos a una lista de diccionarios
        # Recuperar los datos de productos de request.POST
        productos_facturacion = request.POST.get('productos_json')
        # Convertir los datos de productos de JSON a un objeto de Python
        productos_fac = []
        
        # Verificar si hay datos en el localStorage
        if productos_facturacion:
            # Analizar la cadena JSON para obtener la lista de productos
            productos_a_facturar = json.loads(productos_facturacion)

            for producto in productos_a_facturar:
                # Aquí puedes acceder a cada atributo del producto
                id_producto = producto['id']
                colorCompleto = producto['color']
                color = colorCompleto.split('(')[0].strip() # Divide la cadena en dos partes y toma la primera parte (el color)
                codigo = producto['codigo']
                cantidad = producto['cantidad']
                cantidad_decimal = Decimal(str(cantidad))
                
                try:
                    producto_bd = Producto.objects.get(id=id_producto)
                    # Realiza las operaciones necesarias con el producto obtenido
                except Producto.DoesNotExist:
                    return JsonResponse({'error': 'Datos no encontrados'}, )
                #reviso si producto tiene oferta
                if (producto_bd.precio_oferta):
                    precio = producto_bd.precio_oferta
                    preciot = producto_bd.precio_oferta * cantidad_decimal
                else:
                    precio = producto_bd.precio
                    preciot = producto_bd.precio * cantidad_decimal
                productos_fac.append({
                    'id': producto_bd.id,
                    'modelo': producto_bd.modelo,
                    #'marca': marca_info,
                    'color':color,
                    'codigo':codigo,
                    'cantidad':cantidad,
                    'precio': precio,
                    'detalle': producto_bd.detalle,
                    'preciot':preciot
                    # Agrega otros campos que necesites
                })
        fecha_hora_actual = timezone.now()
        # Generar número de factura
        with transaction.atomic():  # Inicia una transacción atómica
        # Generar número de factura
            ultima_factura = Factura.objects.select_for_update().last()  # Bloquea la última factura para evitar conflictos
            numero_factura = ultima_factura.id + 1 if ultima_factura else 1

            # Guardar la nueva factura en la base de datos
            nueva_factura = Factura.objects.create(id=numero_factura)
        context = {
            'nombre':nombre,
            'apellidos':apellidos,
            'cedula':cedula,
            'email':email,
            'celular':celular,
            'ciudad':ciudad,
            'direccion':direccion,
            'direccionEnvio':direccionEnvio,
            'productos': productos_fac,
            'subtotal':subtotal,
            'porcentaje':porcentaje,
            'descuento':descuento,
            'subtotalD':subtotalD,
            'porcentajeDescuento':porcentajeDescuento,
            'iva':iva,
            'total':total,
            'tipoPago':tipoPago,
            'peso':peso,
            'fecha':fecha_hora_actual,
            'numeroCheque':numeroCheque,
            'numeroFactura':numero_factura
        }
        
        #return render(request, 'reciboPago.html',context)
        html_content = render_to_string('reciboPagoPdf.html', context)

        # Guardar el contenido HTML en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
            temp_html.write(html_content.encode('utf-8'))
            temp_html_path = temp_html.name

        # Configuración de pdfkit
        config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        
        # Personalizar el nombre del archivo PDF
        # Personalizar el nombre del archivo PDF
        nombre_archivo_pdf = 'Factura_{}_{}_{}.pdf'.format(numero_factura, nombre, apellidos)

        # Convertir el archivo HTML temporal a PDF
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=nombre_archivo_pdf).name
        pdfkit.from_file(temp_html_path, output_path, configuration=config)

        #enviar por correo el pdf
        destinatario = email  # O la dirección de correo electrónico a la que deseas enviar el correo
        asunto = 'Facturacion emitida por PC Computers'
        cuerpo = 'Adjunto encontrarás la factura emitida por PC Computers.'
        archivo_adjunto = output_path
        # Crear mensaje de correo electrónico
        mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
        # Adjuntar archivo PDF
        archivo_adjunto = open(archivo_adjunto, 'rb')
        mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
        # Enviar correo electrónico
        try:
            # Envía el correo electrónico
            mensaje.send()
            #para bajar el stock
            for prod in productos_a_facturar:
                codigo_producto = prod['codigo']
                cantidad_producto = prod['cantidad']
                try:
                    producto_stock = ColorStock.objects.get( codigo_articulo=codigo_producto)
                    nuevo_stock = int(producto_stock.stock) - int(cantidad_producto)
                    producto_stock.stock = nuevo_stock
                    producto_stock.save()
                except ColorStock.DoesNotExist:
                    print('debo bajar el stock mediante id y color')
            
            print("Correo electrónico enviado correctamente a:", destinatario)
        except ValidationError as e:
            print("Error de validación al enviar el correo electrónico:", e)
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
        
        
        
        # Realizar la consulta para obtener el usuario con el número de cédula dado
        try:
            usuario_adicional = adicionalUsuario.objects.get(cedula=cedula)
            # Si se encuentra un usuario con el número de cédula dado, 'usuario' contendrá ese objeto adicionalUsuario
            usuario_adicional.direccion = direccion
            usuario_adicional.direccionEnvio = direccionEnvio
            usuario_adicional.celular = celular
            usuario_adicional.ciudad = ciudad
            usuario_adicional.save()
            
            # Obtener el usuario asociado al usuario adicional
            usuario = usuario_adicional.user

            # Actualizar los campos del usuario con los nuevos valores
            usuario.first_name = nombre
            usuario.last_name = apellidos
            usuario.email = email

            # Guardar los cambios en el usuario
            usuario.save()
            
            
        except adicionalUsuario.DoesNotExist:
            # Si no se encuentra ningún usuario con el número de cédula dado, se lanzará una excepción adicionalUsuario.DoesNotExist
            # Aquí puedes manejar el caso en el que no se encuentre ningún usuario con el número de cédula dado
            usuario = User.objects.create_user(username=cedula, email=email)
            usuario.first_name = nombre
            usuario.last_name = apellidos
            usuario.is_active = False
            usuario.save()
            
            adicionalU = adicionalUsuario()
            adicionalU.user = usuario
            adicionalU.cedula = cedula
            adicionalU.celular = celular
            adicionalU.ciudad = ciudad
            adicionalU.direccion = direccion
            adicionalU.direccionEnvio = direccionEnvio
            adicionalU.save()
            
        #para crear el registro
        try:
            with transaction.atomic():
                nuevoRegistro = Registro()
                nuevoRegistro.usuario = usuario
                nuevoRegistro.fecha_hora = fecha_hora_actual
                total = total.replace(",", ".")
                total = Decimal(total)
                nuevoRegistro.total_vendido = total
                descuento = descuento.replace(",", ".")
                descuento = Decimal(descuento)
                nuevoRegistro.total_descuento = descuento
                user_id = request.user.id
                nuevoRegistro.vendedor_id = user_id
                nuevoRegistro.save()
        except Exception as e:
            # Imprime la excepción para conocer el tipo y los detalles del error
            print("Error al guardar el registro:", e)
        
        # Devolver el PDF como una respuesta HTTP
        with open(output_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="recibo_pago.pdf"'
            
            # Agregar un script JavaScript para limpiar la pantalla después de la descarga
            response.write("<script>localStorage.removeItem('productos_facturacion');</script>")
            
        return response
    # Renderiza tu plantilla como lo haces normalmente
    else:
        # Si no es una solicitud POST, retornar una respuesta de error
        return HttpResponse("Error: Esta vista solo acepta solicitudes POST.")

