from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from ventas.decorators import vendedor_required
from django.contrib.auth.models import User, Group
from inicio.models import adicionalUsuario, Iva, DescuentoServicio
from operacion.models import Gasto, Ingreso
from productos.models import Producto, ColorStock
from operacion.models import Caja
from .models import Registro, Factura, FacturaCompleta, FacturaXML, Deudas, Pago, FacturaCredito, Servicio, PagoServicio, PagoServicioCombinado, PagoRegistroCombinado, PagoPendienteCombinado, Equipo, DescripcionEquipo
import json
from django.http import JsonResponse, FileResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.http import HttpResponse
from django.db import transaction
from datetime import date, datetime, timedelta
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
import base64
import os
from django.contrib import messages
from django.http import Http404
from django.utils import timezone as dj_timezone

import tempfile
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models import Q
from weasyprint import HTML
from io import BytesIO
#SRI
from ventas.utils.sri import generar_clave_acceso, construir_factura_xml, firmar_xml_xades, enviar_a_sri_y_autorizar, debug_verificar_referencias, verificar_firma_local, extraer_ruc_xml, derivar_ruc_desde_cert
import os, random, io
from barcode import Code128
from barcode.writer import ImageWriter
import logging
from zoneinfo import ZoneInfo
import threading

    
@vendedor_required
def inicio_ventas(request):
    
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
    
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
            todosProductos = Producto.objects \
            .filter(colores__isnull=False) \
            .exclude(desactivado="si") \
            .prefetch_related('colores') \
            .distinct()
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
        
        # Obtener el grupo de vendedores
        vendedor_group = Group.objects.get(name='Vendedores')

        # Obtener todos los usuarios que pertenecen al grupo de vendedores
        usuarios_vendedores = User.objects.filter(groups__in=[vendedor_group])

        return render(request, 'ventas_inicio.html', {"usuarios":usuarios_json, "todosProductos":todosProductos, "usuarios_vendedores":usuarios_vendedores,"caja":caja})
    except Caja.DoesNotExist:
        return render(request, 'ventas_inicio.html',{})
    

@vendedor_required
def registro_servicios(request):
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
    
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
        
        # Obtener el grupo de Tecnicos
        tecnicos_group = Group.objects.get(name='Tecnicos')

        # Obtener todos los usuarios que pertenecen al grupo de vendedores
        tecnicos = User.objects.filter(groups__in=[tecnicos_group])
        
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
           
        try:
            registros = Servicio.objects.order_by('-id')[:5]
        except Servicio.DoesNotExist:
            registros =''

        try:
            descuento_servicio = DescuentoServicio.objects.latest('id')
            porcentaje_descuento = descuento_servicio.porcentaje
        except DescuentoServicio.DoesNotExist:
            porcentaje_descuento = 0
        
        try:
            equipo = Equipo.objects.all()
            descripcionEquipo = DescripcionEquipo.objects.all()
            #print(descripcionEquipo)
            #print(equipo)
        except Equipo.DoesNotExist:
            equipo = ''
        except DescripcionEquipo.DoesNotExist:
            descripcionEquipo = ''
        
        return render(request, 'registro_servicios.html', {"usuarios":usuarios_json, "tecnicos":tecnicos,"caja":caja,"fecha":fecha_actual,'porcentaje_descuento':porcentaje_descuento,"equipos":equipo,"descripcionEquipo":descripcionEquipo,"registros":registros})
    except Caja.DoesNotExist:
        return render(request, 'registro_servicios.html',{})
    
def generar_recibo_servicios(request):
    if request.method == 'POST':
        # Recuperar todos los datos del formulario
        cedula = request.POST.get('cedula')
        celular = request.POST.get('celular')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        ciudad = request.POST.get('ciudad')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        direccion_envio = request.POST.get('direccionEnvio')
        #fecha_entrega = request.POST.get('fecha_entrega')
        tipo_servicio = request.POST.get('tipo_servicio')
        equipo = request.POST.get('tipo_equipo')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        serie = request.POST.get('serie')
        #descripcion_problema = request.POST.get('descripcion_problema')
        solucion = request.POST.get('solucion')
        tecnico_asignado = request.POST.get('tecnico_asignado')
        #usuario_recepta = request.POST.get('usuario_recepta')
        costo = request.POST.get('costo')
        descuento = 0
        try:
            descuento_servicio = DescuentoServicio.objects.latest('id')
            porcentaje_descuento = descuento_servicio.porcentaje
        except DescuentoServicio.DoesNotExist:
            porcentaje_descuento = 0
        try:
            auxCliente = adicionalUsuario.objects.get(cedula = cedula)
            #recupero el ultimo servicio del usuario para poner el contador para descuentos
            try:
                # Filtrar por usuario y obtener el último servicio basado en el campo 'id'
                ultimo_servicio_usuario = Servicio.objects.filter(usuario=auxCliente.user).latest('id')
                
                if ultimo_servicio_usuario.numero_reparacion ==1:
                    numero_servicios = 2
                elif ultimo_servicio_usuario.numero_reparacion ==2:
                    numero_servicios = 3
                    descuento = Decimal(costo) * (Decimal(porcentaje_descuento)/100)
                    costo = Decimal(costo) - descuento
                elif ultimo_servicio_usuario.numero_reparacion ==3:
                    numero_servicios = 1
            except Servicio.DoesNotExist:
                numero_servicios = 1
        except adicionalUsuario.DoesNotExist:
            return 
        
        costoAux = Decimal(costo) + descuento
        
        if equipo == 'Otro':
            otroEquipo = request.POST.get('otro_equipo_texto')
            equipo = equipo + ' ('+ (otroEquipo or '')+')'
            descripcion_problema = request.POST.get('descripcion_otro')
            
        else:    
            descripcion_problema = request.POST.get('problemas_resolver')
            
        if descripcion_problema == 'Otro':
            otroProblema = request.POST.get('descripcion_otro')
            descripcion_problema = descripcion_problema+' - '+otroProblema
        
        #fecha_hora_actual = timezone.now()
        fecha_hora_actual = dj_timezone.now()
        
                
        
        # Realizar la consulta para obtener el usuario con el número de cédula dado
        try:
            usuario_adicional = adicionalUsuario.objects.get(cedula=cedula)
            # Si se encuentra un usuario con el número de cédula dado, 'usuario' contendrá ese objeto adicionalUsuario
            usuario_adicional.direccion = direccion
            usuario_adicional.celular = celular
            usuario_adicional.ciudad = ciudad
            #usuario_adicional.deuda = 'si'
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
            adicionalU.direccionEnvio = direccion
            #adicionalU.deuda = 'si'
            adicionalU.save()
            
       
        
        nuevoservicio = Servicio()
        usuario_adicional = adicionalUsuario.objects.get(cedula=cedula)
        nuevoservicio.usuario = usuario_adicional.user
        #para el cajero
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        nuevoservicio.caja = caja
        nuevoservicio.tipo_servicio = tipo_servicio
        nuevoservicio.equipo = equipo
        nuevoservicio.marca = marca
        nuevoservicio.modelo = modelo
        nuevoservicio.serie = serie
        nuevoservicio.descripcion_problema = descripcion_problema
        if solucion:
            nuevoservicio.solucion = solucion
        nuevoservicio.tecnico_asignado = tecnico_asignado
        nuevoservicio.usuario_recepta= request.user
        nuevoservicio.costo = costo
        nuevoservicio.costo_sin_descuento = costoAux
        nuevoservicio.saldo = costo
        nuevoservicio.numero_reparacion = numero_servicios
        nuevoservicio.save()
        
        
        
        
        id = nuevoservicio.id  # Utiliza 'id' en lugar de 'fecha_ingreso'
            
        
        context = {
            'id':id,
            'cedula': cedula,
            'celular': celular,
            'nombre': nombre,
            'apellidos': apellidos,
            'ciudad': ciudad,
            'email': email,
            'direccion': direccion,
            'direccion_envio': direccion_envio,
            'fecha_ingreso': fecha_hora_actual,
            #'fecha_entrega': fecha_entrega,
            'tipo_servicio': tipo_servicio,
            'equipo': equipo,
            'marca': marca,
            'modelo': modelo,
            'serie': serie,
            'descripcion_problema': descripcion_problema,
            'solucion': solucion,
            'tecnico_asignado': tecnico_asignado,
            'usuario_recepta': request.user,
            'costo': costo,
            'saldo':costo
        }
        
        
        
        ####### PARA WHTMLTOPDF #######
        #generar pdf y enviar
        #html_content = render_to_string('registro_servicios_recibo.html', context)

        # Guardar el contenido HTML en un archivo temporal
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
        #    temp_html.write(html_content.encode('utf-8'))
        #    temp_html_path = temp_html.name
            
            # Cerrar el archivo HTML temporal
        #    temp_html.close()
            # Eliminar el archivo PDF temporal
       

        # Configuración de pdfkit
        #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
       

        # Convertir el archivo HTML temporal a PDF
        #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        #pdfkit.from_file(temp_html_path, output_path, configuration=config)

        ##### PARA WEASYPRINT   ######
        #generar pdf y enviar
        html_content = render_to_string('registro_servicios_recibo.html', context)

        # Convertir directamente a PDF usando WeasyPrint
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
        output_path = tempfile.mktemp(suffix='.pdf')    
        HTML(string=html_content).write_pdf(output_path)
            

        # Codificar la ruta
        encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
        


        #enviar por correo el pdf
        destinatario = email  # O la dirección de correo electrónico a la que deseas enviar el correo
        asunto = 'Recibo de recepción de equipo - PC Computers'
        cuerpo = 'Adjunto encontrarás el recibo de recepción de equipo por PC Computers.'
        archivo_adjunto = output_path
        # Crear mensaje de correo electrónico
        mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
        # Adjuntar archivo PDF
        archivo_adjunto = open(archivo_adjunto, 'rb')
        mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
        archivo_adjunto.close()
        # Enviar correo electrónico
    
        try:
            # Envía el correo electrónico
            mensaje.send()        
            print("Correo electrónico enviado correctamente a:", destinatario)
        except ValidationError as e:
            print("Error de validación al enviar el correo electrónico:", e)
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
        

        
        
        #context['archivo_pdf'] = archivo_adjunto.read()
       
        # Agregar el contenido del PDF al contexto
        #context['archivo_pdf'] = pdf_content
        # Después de enviar el correo electrónico exitosamente
        # Devolver el PDF como una respuesta HTTP
        #encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
            
        context = {'encoded_path': encoded_path}
        return render(request, 'descargar_pdf_servicios.html', context)
        
        

    else:
        # Manejar el caso de solicitud GET si es necesario
        return HttpResponse('Solicitud GET no permitida en esta vista')

@vendedor_required
def descargar_pdf_servicios(request, encoded_path):
    # Decodificar la ruta del archivo
    decoded_path = urlsafe_base64_decode(encoded_path).decode('utf-8')
    
    with open(decoded_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="recibo_recepcion_equipo.pdf"'
    return response

@vendedor_required
def generardescarga_pdf_servicios(request, encoded_path):
    # Decodificar la ruta del archivo
    context = {'encoded_path': encoded_path}
    return render(request, 'descargar_pdf_servicios.html', context)

@vendedor_required
def nuevo_abono(request, id_servicio):
    # Decodificar la ruta del archivo
    try:
        servicio = Servicio.objects.get(id = id_servicio)
    except Servicio.DoesNotExist:
        servicio = ''
        
    try:
        pagoServicio = PagoServicio.objects.filter(servicio = servicio)
    except Servicio.DoesNotExist:
        pagoServicio = ''
    
    return render(request, 'registro_servicios_abono.html',{"servicio":servicio,"pagoServicio":pagoServicio})

@vendedor_required
def generarrecibo_nuevo_abono(request):
    if request.method == 'POST':
        abono = request.POST.get('pago')
        servicio_id = request.POST.get('servicio_id')
        
        try:
            servicio = Servicio.objects.get(id=servicio_id)
        except Servicio.DoesNotExist:
            return render(request, 'ventas_servicios_abono.html',{})
        
        tipoPago = request.POST.get('tipoPago')
        
        nuevoAbono = PagoServicio()
        
        if tipoPago == 'Cheque':
            banco = request.POST.get('Banco')
            if banco == 'Otro':
                banco = request.POST.get('otroBanco')
            numeroCheque = request.POST.get('numeroCheque')
            nuevoAbono.banco = banco
            nuevoAbono.numeroCheque = numeroCheque
        elif tipoPago == 'Transferencia':
            numeroTransferencia  = request.POST.get('numeroTransferencia')
            nuevoAbono.numeroTransferencia = numeroTransferencia
        elif tipoPago == 'Combinado':
            servicioCombinado = PagoServicioCombinado()
            if request.POST.get('check1'):  # Verifica si el checkbox está marcado
                valorE = request.POST.get('input1')
                if valorE:
                    servicioCombinado.valorEfectivo = valorE

            if request.POST.get('check2'):  # Verifica si el checkbox está marcado
                valorTc = request.POST.get('input2')
                if valorTc:
                   servicioCombinado.valorTarjetaCredito = valorTc

            if request.POST.get('check3'):  # Verifica si el checkbox está marcado
                valorC = request.POST.get('input3')
                if valorC:
                    servicioCombinado.valorCheque = valorC

            if request.POST.get('check4'):  # Verifica si el checkbox está marcado
                valorF = request.POST.get('input4')
                if valorF:
                    servicioCombinado.valorTransferencia = valorF
    
            if request.POST.get('check5'):  # Verifica si el checkbox está marcado
                valorTd = request.POST.get('input5')
                if valorTd:
                   servicioCombinado.valorTarjetaDebito = valorTd
        #else:
        
        adicionalU = adicionalUsuario.objects.get(user = servicio.usuario)
        
        try:
            pagosServicio = PagoServicio.objects.filter(servicio=servicio)
        except PagoServicio.DoesNotExist:
            pagosServicio = ''
        fecha_hora_actual =  dj_timezone.now()
        
        #para el cajero
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        
       
        nuevoAbono.servicio = servicio
        nuevoAbono.caja = caja
        nuevoAbono.abono = abono
        nuevoAbono.tipoPago = tipoPago
        nuevoAbono.save()
        
        if tipoPago == 'Combinado':
            servicioCombinado.pagoServicio = nuevoAbono
            servicioCombinado.save()
            
        if servicio.abonado:
            totalAbonado = Decimal(servicio.abonado) + Decimal(abono)
        else:
            totalAbonado = abono
        
        servicio.abonado = totalAbonado 
        
        saldo = Decimal(servicio.costo) - Decimal(totalAbonado)
        servicio.saldo = saldo
        
        servicio.save()
        
        context = {
            'nombre': servicio.usuario.first_name,
            'apellidos': servicio.usuario.last_name,
            'cedula':adicionalU.cedula,
            'ciudad':adicionalU.ciudad,
            'direccion':adicionalU.direccion,
            'celular':adicionalU.celular,
            'email':servicio.usuario.email,
            'servicio':servicio,
            'pagosServicio':pagosServicio,
            'fecha':fecha_hora_actual,
            'abono':abono,
            'tipoPago':tipoPago,
            'totalAbonado':totalAbonado,
            'saldo':saldo
        }
        
        ###         PARA WHTMLTOPDF
        #generar pdf y enviar
        #html_content = render_to_string('registro_servicios_reciboabono.html', context)

        # Guardar el contenido HTML en un archivo temporal
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
        #    temp_html.write(html_content.encode('utf-8'))
        #    temp_html_path = temp_html.name
            
            # Cerrar el archivo HTML temporal
        #    temp_html.close()
            # Eliminar el archivo PDF temporal
       

        # Configuración de pdfkit
        #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
       

        # Convertir el archivo HTML temporal a PDF
        #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        #pdfkit.from_file(temp_html_path, output_path, configuration=config)

        #### PARA WEASYPRINT
        # Generar PDF y enviar
        html_content = render_to_string('registro_servicios_reciboabono.html', context)

        # Convertir directamente a PDF usando WeasyPrint
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
        output_path = tempfile.mktemp(suffix='.pdf')   
        HTML(string=html_content).write_pdf(output_path)
            

        # Codificar la ruta
        #encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                

        #enviar por correo el pdf
        destinatario = servicio.usuario.email  # O la dirección de correo electrónico a la que deseas enviar el correo
        asunto = 'Recibo de abono por servicio - PC Computers'
        cuerpo = 'Adjunto encontrarás el recibo de recepción de equipo por PC Computers.'
        archivo_adjunto = output_path
        # Crear mensaje de correo electrónico
        mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
        # Adjuntar archivo PDF
        archivo_adjunto = open(archivo_adjunto, 'rb')
        mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
        archivo_adjunto.close()
        # Enviar correo electrónico
    
        try:
            # Envía el correo electrónico
            mensaje.send()        
            print("Correo electrónico enviado correctamente a:", destinatario)
        except ValidationError as e:
            print("Error de validación al enviar el correo electrónico:", e)
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
            
        encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
            
        context = {'encoded_path': encoded_path,'id':servicio.id}
        return render(request, 'descargar_pdf_servicios_abono.html', context)
        
        return render(request, 'registro_servicios_reciboabono.html',context)
    else:
        # Manejar el caso de solicitud GET si es necesario
        return HttpResponse('Solicitud no permitida en esta vista')

@vendedor_required
def politica_servicios(request):
    # Decodificar la ruta del archivo
    
    return render(request, 'ventas_servicios_politica.html')


#@require_http_methods(["GET", "POST"])  # Agrega los métodos que necesites manejar

@vendedor_required
def servicios_registros(request):
    try:
        descuento_servicio = DescuentoServicio.objects.latest('id')
        porcentaje_descuento = descuento_servicio.porcentaje
    except DescuentoServicio.DoesNotExist:
        porcentaje_descuento = 0
    if request.method == 'POST':
        query = request.POST.get('query')
        #consulta basica
        #registros = Servicio.objects.filter(
        #Q(id__icontains=query) |
        #Q(equipo__icontains=query) |
        #Q(marca__icontains=query) |
        #Q(modelo__icontains=query) |
        #Q(serie__icontains=query))
        # Separar los términos de búsqueda
        search_terms = query.split()

        # Inicializar la consulta Q
        query_filter = Q()

        # Agregar filtros para cada término en cada campo específico
        for term in search_terms:
            term_filter = (
                Q(id__icontains=query) |
                Q(marca__icontains=term) |
                Q(modelo__icontains=term) |
                Q(serie__icontains=term) |
                Q(equipo__icontains=term) |
                Q(usuario__first_name__icontains=term) |
                Q(usuario__last_name__icontains=term)
            )
            query_filter &= term_filter
        
        # Filtrar los registros basados en la consulta Q construida
        registros = Servicio.objects.filter(query_filter)
        
        return render(request, 'registro_servicios_lista.html',{"registros":registros,"porcentaje_descuento":porcentaje_descuento,"busqueda":query})
    else:
        option_value = request.GET.get('option', None)
        if (option_value == 'todo'):
            try:
                registros = Servicio.objects.all().order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
            
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        elif(option_value == 'hoy'):
            try:
                registros = Servicio.objects.filter(fecha_ingreso=date.today()).order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
            
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        elif(option_value == 'semana'):
            # Obtener la fecha de inicio de la semana (lunes)
            hoy = datetime.today()
            inicio_semana = hoy - timedelta(days=hoy.weekday())

            # Obtener la fecha de fin de la semana (domingo)
            fin_semana = inicio_semana + timedelta(days=6)

            # Filtrar los registros por el rango de fechas de la semana
            try:
                registros = Servicio.objects.filter(fecha_ingreso__date__range=[inicio_semana, fin_semana]).order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
            
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        elif(option_value == 'mes'):
            # Obtener el primer día del mes actual
            primer_dia_mes = datetime.now().replace(day=1)

            # Obtener el último día del mes actual
            ultimo_dia_mes = primer_dia_mes.replace(day=1, month=primer_dia_mes.month+1) - timedelta(days=1)

            # Filtrar los registros por el rango de fechas del mes actual
            try:
                registros = Servicio.objects.filter(fecha_ingreso__date__range=[primer_dia_mes, ultimo_dia_mes]).order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
            
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        
        elif(option_value == 'terminados'):
            try:
                registros = Servicio.objects.filter(estado='terminado').order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
                
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        
        
        elif(option_value == 'pendiente'):
            try:
                registros = Servicio.objects.filter(estado='pendiente').order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
                
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})
        
        else:
            try:
                registros = Servicio.objects.all().order_by('-id')
            except Servicio.DoesNotExist:
                registros = ''
            
            return render(request, 'registro_servicios_lista.html', {"registros":registros,"option":option_value,"porcentaje_descuento":porcentaje_descuento})

@vendedor_required
def finalizar_servicio(request):
    if request.method == 'POST':
        servicio_id = request.POST.get('id')
        costo = request.POST.get('costo')
        abono = request.POST.get('abono')
        solucion = request.POST.get('solucion')
        problema = request.POST.get('problema')
        estado = request.POST.get('estado')

        print('costo ',costo)
        print('abono', abono)
        print('solucion ',solucion)
        
        saldo = Decimal(costo) - Decimal(abono)

        servicio = get_object_or_404(Servicio, pk=servicio_id)

        fecha_hora_actual = dj_timezone.now()
        # Actualizar los campos del servicio
        servicio.costo = costo
        servicio.abono = abono
        servicio.solucion = solucion
        if problema:
            servicio.descripcion_problema = problema
        servicio.fecha_entrega = fecha_hora_actual
        servicio.saldo = saldo
        if estado == 'terminado':
            servicio.estado = 'terminado'  # Puedes ajustar tu lógica según tus necesidades
            estado = 'actualizacion'

        servicio.save()
        
        usuario = adicionalUsuario.objects.get(user = servicio.usuario)
        
        
        context = {
            'id':servicio_id,
            'cedula': usuario.cedula,
            'celular': usuario.celular,
            'nombre': servicio.usuario.first_name,
            'apellidos': servicio.usuario.last_name,
            'ciudad': usuario.ciudad,
            'email': servicio.usuario.email,
            'direccion': usuario.direccion,
            'direccion_envio': usuario.direccionEnvio,
            'fecha_ingreso': fecha_hora_actual,
            #'fecha_entrega': fecha_entrega,
            'tipo_servicio': servicio.tipo_servicio,
            'equipo': servicio.equipo,
            'marca': servicio.marca,
            'modelo': servicio.modelo,
            'serie': servicio.serie,
            'descripcion_problema': problema,
            'solucion': solucion,
            'tecnico_asignado': servicio.tecnico_asignado,
            'usuario_recepta': servicio.usuario_recepta,
            'costo': costo,
            'abono': abono,
            'saldo':saldo,
            'estado': estado
        }
        
        ###         PARA WHTMLTOPDF
        #generar pdf y enviar
        #html_content = render_to_string('registro_servicios_recibo.html', context)

        # Guardar el contenido HTML en un archivo temporal
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
        #    temp_html.write(html_content.encode('utf-8'))
        #    temp_html_path = temp_html.name
            
            # Cerrar el archivo HTML temporal
        #    temp_html.close()
            # Eliminar el archivo PDF temporal
       

        # Configuración de pdfkit
        #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
       

        # Convertir el archivo HTML temporal a PDF
        #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        #pdfkit.from_file(temp_html_path, output_path, configuration=config)

        #### PARA WEASYPRINT
        # Generar PDF y enviar
        html_content = render_to_string('registro_servicios_recibo.html', context)

        # Convertir directamente a PDF usando WeasyPrint
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
        output_path = tempfile.mktemp(suffix='.pdf')   
        HTML(string=html_content).write_pdf(output_path)
            

        # Codificar la ruta
        #encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                

        #enviar por correo el pdf
        destinatario = servicio.usuario.email  # O la dirección de correo electrónico a la que deseas enviar el correo
        asunto = 'Recibo de recepción de equipo - PC Computers'
        cuerpo = 'Adjunto encontrarás el recibo de recepción de equipo por PC Computers.'
        archivo_adjunto = output_path
        # Crear mensaje de correo electrónico
        mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
        # Adjuntar archivo PDF
        archivo_adjunto = open(archivo_adjunto, 'rb')
        mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
        archivo_adjunto.close()
        # Enviar correo electrónico
    
        try:
            # Envía el correo electrónico
            mensaje.send()        
            print("Correo electrónico enviado correctamente a:", destinatario)
        except ValidationError as e:
            print("Error de validación al enviar el correo electrónico:", e)
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
        
        # Suponiendo que tienes output_path definido y quieres codificarlo
        encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))

        # Crear el diccionario de contexto
        context = {'encoded_path': encoded_path}

        # Devolver JsonResponse con el contexto
        return JsonResponse(context)

    # Manejar otros métodos HTTP si es necesario
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@vendedor_required
def cancelar_servicio(request):
    if request.method == 'POST':
        # Extraer el ID del servicio desde los datos POST
        servicio_id = request.POST.get('id')
        
        # Asegurarse de que el ID esté presente
        if not servicio_id:
            return JsonResponse({'error': 'ID del servicio no proporcionado'}, status=400)

        # Recuperar el servicio usando el ID
        servicio = get_object_or_404(Servicio, id=servicio_id)
        
        # Aquí puedes marcar el servicio como cancelado o realizar otra acción
        servicio.estado = 'cancelado'  # Suponiendo que tienes un campo `cancelado` en el modelo
        servicio.save()

        # Devolver una respuesta JSON de éxito
        if servicio.abonado is not None and servicio.abonado > 0:
            devolver_abono = 'si'
        else:
            devolver_abono = 'no'
        context = {
            'devolver_abono':devolver_abono,
            'valor':servicio.abonado,
            'datos':servicio.usuario.last_name + ' '+servicio.usuario.first_name
        }
        return JsonResponse(context)
        
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@vendedor_required
def home_ventas(request):
    
    return render(request, 'ventas_home.html', {})

@vendedor_required
def gastos_ventas(request):
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        
        try:
            gastos = Gasto.objects.filter(caja = caja)
            ingresos = Ingreso.objects.filter(caja = caja)
        except Gasto.DoesNotExist:
            gastos = ''
        except Ingreso.DoesNotExist:
            ingresos = ''
        
        
        if request.method == 'POST':
            tipo = request.POST.get('tipo')
            valor = request.POST.get('valor')
            descripcion = request.POST.get('descripcion')
            
            if (tipo == 'gasto'):
                # Crea el objeto Gasto
                nuevo_gasto = Gasto(
                    valor=valor,
                    descripcion=descripcion,
                    caja = caja,
                    usuario = request.user
                )
                nuevo_gasto.save()
                gastos = Gasto.objects.filter(caja = caja)
            else:
                nuevo_ingreso = Ingreso(
                    valor=valor,
                    descripcion=descripcion,
                    caja = caja,
                    usuario = request.user
                )
                nuevo_ingreso.save()
                ingresos = Ingreso.objects.filter(caja = caja)
            return render(request, 'ventas_gastos.html', {'caja':caja,'gastos':gastos,'ingresos':ingresos})
        return render(request, 'ventas_gastos.html', {'caja':caja,'gastos':gastos,'ingresos':ingresos})
    except Caja.DoesNotExist:
        return render(request, 'ventas_gastos.html', {})
    


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
                    #producto_bd = Producto.objects.get(id=id_producto)
                    producto_bd = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=id_producto)
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

# --- Diagnóstico básico de P12 vs RUC, validez y cadena ---
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from datetime import datetime
import re

def diagnostico_certificado_p12(p12_path: str, p12_pass: str, ruc_esperado: str) -> dict:
    """
    Abre el .p12 y devuelve info útil:
      - sujeto, issuer, rango de validez, número de serie
      - RUC extraído de subject (serialNumber o 2.5.4.5)
      - match con RUC esperado
    """
    with open(p12_path, "rb") as f:
        p12_data = f.read()
    key, cert, chain = pkcs12.load_key_and_certificates(
        p12_data, p12_pass.encode("utf-8")
    )

    if cert is None:
        return {"ok": False, "error": "El P12 no contiene certificado"}

    info = {}
    info["subject"] = cert.subject.rfc4514_string()
    info["issuer"] = cert.issuer.rfc4514_string()
    info["not_before"] = cert.not_valid_before
    info["not_after"] = cert.not_valid_after
    info["serial_number"] = hex(cert.serial_number)

    # Intenta extraer RUC del subject: suele ir en serialNumber o OID 2.5.4.5
    ruc_en_cert = None
    for attr in cert.subject:
        oid = attr.oid.dotted_string
        name = attr.oid._name if hasattr(attr.oid, "_name") else oid
        val = attr.value.strip()
        if name in ("serialNumber",) or oid == "2.5.4.5":
            # suele venir solo dígitos; si viniera con prefijo, filtramos
            m = re.search(r"(\d{13})", val)
            if m:
                ruc_en_cert = m.group(1)
                break
    info["ruc_en_cert"] = ruc_en_cert
    info["ruc_coincide"] = (ruc_en_cert == str(ruc_esperado))

    # Validez temporal (UTC)
    ahora = dj_timezone.now().astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

    info["vigente"] = (
        cert.not_valid_before <= ahora <= cert.not_valid_after
    )

    return {"ok": True, **info}


def reciboPago(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        tipoPago = request.POST.get('tipoPago')
        tipoVenta = request.POST.get('tipoVenta')
        numeroCheque = request.POST.get('numeroCheque')
        numeroTransferencia = request.POST.get('numeroTransferencia')
        nombreBanco = request.POST.get('nombreBanco')
        cedula = request.POST.get('cedula')
        celular = request.POST.get('celular')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        ciudad = request.POST.get('ciudad')
        direccion = request.POST.get('direccion')
        direccionEnvio = request.POST.get('direccionEnvio')
        email = request.POST.get('email')
        descuento = request.POST.get('descuento')
        usuarioVendedor = request.POST.get('usuarioVendedor')
        
        # 🔍 Validación de identificación (cédula o RUC)
        es_valida, tipo_ident = es_identificacion_valida_cedula_o_ruc(cedula)

        if not es_valida:
            messages.success(request, "Cédula/RUC incorrectos, intente nuevamente por favor.")
            return redirect("/ventas/facturacion")
        
        if (tipoPago == "Combinado"):
            combinados = request.POST.get('combinado')
            # Transformar el JSON en objetos Python
            combinados = json.loads(combinados)
        else:
            combinados = ''


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
                    #producto_bd = Producto.objects.get(id=id_producto)
                    producto_bd = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=id_producto)
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
            
            if (tipoVenta == "Crédito" and tipoPago != "Combinado") or (tipoVenta == "Apartado" and tipoPago != "Combinado"):
                
                abono = request.POST.get('abono')
                print("abonoooooo" + abono)
                abono_int = Decimal(abono) if abono else Decimal(0)
                saldo = totalp - abono_int
                
            elif (tipoVenta == "Crédito" and tipoPago == "Combinado") or (tipoVenta == "Apartado" and tipoPago == "Combinado"):
                abono = 0
                for item in combinados:
                    abono = abono + Decimal(item.get('valor'))
                abono_int = Decimal(abono) if abono else Decimal(0)
                saldo = totalp - abono_int
            else:
                abono = ''
                saldo = ''
             
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
            'tipoVenta':tipoVenta,
            'peso':peso,
            'numeroCheque':numeroCheque,
            'numeroTransferencia':numeroTransferencia,
            'nombreBanco':nombreBanco,
            'combinados':combinados,
            'abono':abono,
            'saldo':saldo,
            'usuarioVendedor':usuarioVendedor
        }
        
        return render(request, 'reciboPago.html', context)
          
    else:
        # Si no es una solicitud POST, retornar una respuesta de error
        return HttpResponse("Error: Esta vista solo acepta solicitudes POST.")  
    
def D(x):
    try:
        return Decimal(str(x))
    except:
        return Decimal("0.00")

def _codigo_numerico():
    """8 dígitos aleatorios para la clave de acceso (puedes usar tu propia lógica)."""
    return f"{random.randint(0,99999999):08d}"

# imports arriba del archivo (una sola vez)
import datetime as dt
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509

def _extraer_ids_sujeto(cert: x509.Certificate) -> dict:
    """
    Devuelve un dict con lo que logremos encontrar en el Subject del certificado:
    - cedula: OID 2.5.4.5 (serialNumber) – en sus logs sale '2.5.4.5=0703074211'
    - ruc: si existe explícito en algún atributo (raro en CN de Ecuador); si no hay, None
    - cn: Common Name
    Retorna {'cedula': str|None, 'ruc': str|None, 'cn': str|None}
    """
    cedula = None
    ruc = None
    cn = None

    for attr in cert.subject:
        oid = attr.oid.dotted_string
        val = str(attr.value).strip()
        # CN
        if oid == x509.oid.NameOID.COMMON_NAME.dotted_string:
            cn = val
        # serialNumber (en muchos certificados ecuatorianos contiene Cédula)
        elif oid == "2.5.4.5":
            # si tiene solo dígitos de 10 caracteres, asúmala como cédula
            if val.isdigit() and len(val) in (10, 13):  # a veces 13 si está como RUC PN
                # si es 13 podría ser RUC de Persona Natural (cédula+001)
                if len(val) == 10:
                    cedula = val
                elif len(val) == 13:
                    # podría ser RUC PN; guárdelo como ruc y también cédula candidata
                    ruc = val
                    cedula = val[:10]
            else:
                cedula = val  # de todas formas guárdela
        # algunos emiten RUC en OID organizacionales; no es estándar
        elif oid in ("2.5.4.10", "2.5.4.11", "2.5.4.15"):
            # intente extraer 13 dígitos seguidos
            import re
            m = re.search(r"\b(\d{13})\b", val)
            if m:
                ruc = m.group(1)

    return {"cedula": cedula, "ruc": ruc, "cn": cn}


def precheck_ruc_cert_xml(p12_bytes: bytes, p12_pass: bytes, xml_bytes: bytes, ruc_config: str) -> dict:
    """
    - No asume que el RUC está en el P12 (en Ecuador muchas veces no está).
    - Compara: RUC settings vs RUC del XML emisor (obligatorio).
    - Extrae cédula/RUC del certificado si es posible (sin romper si no aparece).
    Retorna dict con flags y sin hacer .get() sobre None.
    """
    out = {"ok": True, "mensajes": []}

    # 1) Cargue P12
    try:
        private_key, cert, _chain = pkcs12.load_key_and_certificates(p12_bytes, p12_pass)
        if cert is None:
            out["ok"] = False
            out["mensajes"].append("El .p12 no contiene certificado principal.")
            return out
    except Exception as e:
        out["ok"] = False
        out["mensajes"].append(f"No se pudo abrir el .p12: {e}")
        return out

    # 2) Fechas (evite naive datetimes)
    try:
        # Certificados nuevos (cryptography moderno) ya traen UTC
        not_before = getattr(cert, "not_valid_before_utc", None)
        not_after  = getattr(cert, "not_valid_after_utc",  None)

        # Compatibilidad con certificados antiguos (fechas naive)
        if not_before is None:
            not_before = cert.not_valid_before.replace(tzinfo=ZoneInfo("UTC"))
        if not_after is None:
            not_after = cert.not_valid_after.replace(tzinfo=ZoneInfo("UTC"))

        # Ahora en UTC usando Django
        ahora_utc = dj_timezone.now().astimezone(ZoneInfo("UTC"))

        if not (not_before <= ahora_utc <= not_after):
            out["ok"] = False
            out["mensajes"].append("Certificado fuera de vigencia.")
    except Exception as e:
        out["ok"] = False
        out["mensajes"].append(f"No se pudieron leer fechas del certificado: {e}")


    # 3) Extraiga identificadores del sujeto
    ids = _extraer_ids_sujeto(cert)
    out["cert_subject"] = ids  # {'cedula':..., 'ruc':..., 'cn':...}

    # 4) RUC del XML (obligatorio)
    import lxml.etree as LET
    try:
        root = LET.fromstring(xml_bytes)
        ruc_xml = root.findtext(".//ruc")
        if not ruc_xml:
            out["ok"] = False
            out["mensajes"].append("No se encontró <ruc> del emisor en el XML.")
        out["ruc_xml"] = ruc_xml
    except Exception as e:
        out["ok"] = False
        out["mensajes"].append(f"No se pudo leer el XML para extraer <ruc>: {e}")
        out["ruc_xml"] = None

    # 5) Compare RUC settings vs RUC del XML (esto sí debe coincidir)
    if out.get("ruc_xml") and ruc_config:
        if ruc_config != out["ruc_xml"]:
            out["ok"] = False
            out["mensajes"].append(f"El RUC de settings ({ruc_config}) difiere del RUC del XML ({out['ruc_xml']}).")
    else:
        out["ok"] = False
        out["mensajes"].append("RUC de settings o del XML ausente.")

    # 6) (Informativo) ¿el certificado trae un RUC?
    # No es obligatorio que coincida con el RUC del emisor; a menudo el cert está a nombre de la persona (cédula).
    ruc_cert = ids.get("ruc")  # puede ser None
    if ruc_cert and out.get("ruc_xml"):
        out["ruc_cert_coincide_con_xml"] = (ruc_cert == out["ruc_xml"])
    else:
        out["ruc_cert_coincide_con_xml"] = None  # desconocido/no aplica

    return out

logger = logging.getLogger(__name__)

def enviar_correo_async(mensaje, destinatario):
    """
    Envía el correo electrónico en un hilo separado para no bloquear la respuesta HTTP.
    """
    try:
        mensaje.send()
        logger.info("Correo electrónico enviado correctamente a: %s", destinatario)
    except Exception as e:
        logger.error("Error al enviar el correo electrónico a %s: %s", destinatario, e)
    
def generarPdf(request):
    if request.method == 'POST':
        if 'confirmar_venta' in request.POST:
            now_ec = dj_timezone.now().astimezone(ZoneInfo("America/Guayaquil"))
            fecha_emision_str = now_ec.strftime("%d/%m/%Y")    
            
            
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
            tipoVenta = request.POST.get('tipoVenta')
            usuarioVendedor = request.POST.get('usuarioVendedor')
            abono = request.POST.get('abono')
            saldo = request.POST.get('saldo')
            peso = request.POST.get('peso')
            nombreBanco = request.POST.get('nombreBanco')
            numeroCheque = request.POST.get('numeroCheque')
            numeroTransferencia = request.POST.get('numeroTransferencia')
            combinados = request.POST.get('combinados')
            combinados = combinados.replace("'", "\"")
            combinados_json = json.loads(combinados) if combinados else None
            
            usuario_vendedor_completo = User.objects.get(username=usuarioVendedor)
            
             # Transformar el JSON en objetos Python
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
                    #producto_bd = Producto.objects.get(id=id_producto)
                    producto_bd = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=id_producto)
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
        fecha_hora_actual = datetime.now()
        # Generar número de factura
        with transaction.atomic():  # Inicia una transacción atómica
        # Generar número de factura
            ultima_factura = Factura.objects.select_for_update().last()  # Bloquea la última factura para evitar conflictos
            numero_factura = ultima_factura.id + 1 if ultima_factura else 1

            # Guardar la nueva factura en la base de datos
            nueva_factura = Factura.objects.create(id=numero_factura)

        # --- AHORA sí construimos context (una sola vez) ---
        context = {
            'nombre': nombre,
            'apellidos': apellidos,
            'cedula': cedula,
            'email': email,
            'celular': celular,
            'ciudad': ciudad,
            'direccion': direccion,
            'direccionEnvio': direccionEnvio,
            'productos': productos_fac,
            'subtotal': subtotal,
            'porcentaje': porcentaje,
            'descuento': descuento,
            'subtotalD': subtotalD,
            'porcentajeDescuento': porcentajeDescuento,
            'iva': iva,
            'total': total,
            'tipoPago': tipoPago,
            'peso': peso,
            'fecha': fecha_emision_str,
            'nombreBanco': nombreBanco,
            'numeroCheque': numeroCheque,
            'numeroTransferencia': numeroTransferencia,
            'numeroFactura': numero_factura,
            'combinados': combinados_json,
            'tipoVenta': tipoVenta,
            'abono': abono,
            'saldo': saldo,
            'usuarioVendedor': usuarioVendedor,
        }
        
        # === Verificación/Recalculo de valores ===
        # Si algún valor viene vacío o en cero, lo recalculamos para que el PDF y XML no salgan mal
        if not context.get("subtotal") or D(context["subtotal"]) == 0:
            subtotal_calc = sum(D(p['cantidad']) * D(p['precio']) for p in productos_fac)
            context["subtotal"] = float(subtotal_calc)

        if not context.get("subtotalD") or D(context["subtotalD"]) == 0:
            desc = D(context.get("descuento", 0))
            context["subtotalD"] = float(D(context["subtotal"]) - desc)

        if not context.get("iva") or D(context["iva"]) == 0:
            porc_iva = D(context.get("porcentaje", 12))  # % de IVA por defecto 12 si no viene
            base = D(context["subtotalD"])
            context["iva"] = float((base * porc_iva / 100).quantize(Decimal("0.01")))

        if not context.get("total") or D(context["total"]) == 0:
            context["total"] = float(D(context["subtotalD"]) + D(context["iva"]))

        
        # === Generar PDF (WeasyPrint) para el cliente (independiente del SRI) ===
        if (tipoVenta == 'Crédito') or (tipoVenta == 'Apartado'):
            html_content = render_to_string('ventas_recibopagocredito.html', context)
        else:
            html_content = render_to_string('reciboPagoPdf.html', context)

        pdf_path = tempfile.mktemp(suffix='.pdf')
        HTML(string=html_content).write_pdf(pdf_path)

        # === SRI: Solo intentamos emitir factura electrónica cuando NO es crédito/apartado ===
        xml_aut_path = None
        xml_firmado_path = None
        resultado_sri = None
        
        if (tipoVenta == 'Crédito') or (tipoVenta == 'Apartado'):
            ###         PARA WHTMLTOPDF
            #html_content = render_to_string('ventas_recibopagocredito.html', context)
            # Guardar el contenido HTML en un archivo temporal
            #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
            #    temp_html.write(html_content.encode('utf-8'))
            #    temp_html_path = temp_html.name

            # Configuración de pdfkit
            #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
            
            # Personalizar el nombre del archivo PDF
            # Personalizar el nombre del archivo PDF
            #nombre_archivo_pdf = 'Factura_{}_{}_{}.pdf'.format(numero_factura, nombre, apellidos)

            # Convertir el archivo HTML temporal a PDF
            #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=nombre_archivo_pdf).name
            #pdfkit.from_file(temp_html_path, output_path, configuration=config)

            #### PARA WEASYPRINT
            # Generar PDF y enviar
            html_content = render_to_string('ventas_recibopagocredito.html', context)

            # Convertir directamente a PDF usando WeasyPrint
            output_path = tempfile.mktemp(suffix='.pdf')
            HTML(string=html_content).write_pdf(output_path)

            # Codificar la ruta
            encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                
            
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
            archivo_adjunto.close()
            
            
        else:
            ###         PARA WHTMLTOPDF
            #html_content = render_to_string('reciboPagoPdf.html', context)

            # Guardar el contenido HTML en un archivo temporal
            #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
            #    temp_html.write(html_content.encode('utf-8'))
            #    temp_html_path = temp_html.name

            # Configuración de pdfkit
            #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
            
            # Personalizar el nombre del archivo PDF
            # Personalizar el nombre del archivo PDF
            #nombre_archivo_pdf = 'Factura_{}_{}_{}.pdf'.format(numero_factura, nombre, apellidos)

            # Convertir el archivo HTML temporal a PDF
            #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=nombre_archivo_pdf).name
            #pdfkit.from_file(temp_html_path, output_path, configuration=config)

            # ---- Helpers para comparar fecha de clave vs fecha del XML ----
            import re

            def _dia_clave(clave: str) -> str:
                """Devuelve ddMMyyyy (8 chars) desde la clave acceso (str)."""
                return str(clave)[:8]

            def _dia_xml(xmlb: bytes) -> str:
                """
                Extrae ddMMyyyy desde <fechaEmision> del XML (xmlb en bytes).
                Si no encuentra, devuelve cadena vacía.
                """
                if isinstance(xmlb, str):
                    xmlb = xmlb.encode("utf-8")  # asegúrate que sea bytes

                m = re.search(
                    rb"<fechaEmision>\s*(\d{2})/(\d{2})/(\d{4})\s*</fechaEmision>",
                    xmlb,
                    flags=re.IGNORECASE,
                )
                if not m:
                    return ""
                d, mth, y = (g.decode("utf-8") for g in m.groups())
                return f"{d}{mth}{y}"  # str, no mezclamos bytes


            #### PARA WEASYPRINT
            # Generar PDF y enviar
            buffer = BytesIO()
            html_content = render_to_string('reciboPagoPdf.html', context)

            # Convertir directamente a PDF usando WeasyPrint
            output_path = tempfile.mktemp(suffix='.pdf')
            HTML(string=html_content).write_pdf(output_path)

            # Codificar la ruta
            encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
            
            
            # === EMPIEZA SRI: Generar clave de acceso ===
            # 1) CLAVE DE ACCESO (codDoc '01' = Factura)
            clave_acceso = generar_clave_acceso(
                fecha_emision=fecha_emision_str,
                codDoc="01",
                ruc=settings.SRI_RUC,
                ambiente=settings.SRI_AMBIENTE,     # "1" pruebas, "2" producción
                estab=settings.SRI_ESTAB,           # "001"
                ptoemi=settings.SRI_PTO_EMI,        # "001"
                secuencial=numero_factura,          # <- ahora tolera str o int
                codigo_numerico=_codigo_numerico(), # 8 dígitos
                tipo_emision=settings.SRI_TIPO_EMISION,  # "1" normal
            )
            
            #########3 borrar
            diag = diagnostico_certificado_p12(settings.SRI_P12_PATH, settings.SRI_P12_PASS, settings.SRI_RUC)
            print("DIAG CERT:", diag)
            if not diag.get("ok"):
                print("Cert ERROR:", diag.get("error"))
            if not diag.get("ruc_coincide"):
                print("ATENCIÓN: RUC del P12 no coincide con settings.SRI_RUC")
            if not diag.get("vigente"):
                print("ATENCIÓN: Certificado NO vigente (fechas fuera de rango)")

            ############## asta aqui

            # 2) Construir XML (usa tus reglas de negocio/impuestos). Debe ser versión 1.1.0 e id="comprobante".
            xml_bytes = construir_factura_xml(context, clave_acceso, numero_factura)
            
            # pre check ruc
            # 1) Leer el P12 a bytes
            with open(settings.SRI_P12_PATH, "rb") as fp:
                p12_bytes = fp.read()
            pre = precheck_ruc_cert_xml(p12_bytes, settings.SRI_P12_PASS.encode("utf-8"), xml_bytes, settings.SRI_RUC)
            print("PRECHECK:", pre)
            if not pre.get("ok"):
                # Aquí puede registrar y decidir si continúa o devuelve 400
                # Ejemplo: solo advertir y seguir firmando
                print("PRECHECK advertencias:", pre.get("mensajes"))

        #final pre check 
            
            # 3) Firmar
            xml_firmado = firmar_xml_xades(xml_bytes)
            xml_firmado_path = tempfile.mktemp(suffix=".xml", prefix=f"FAC_{numero_factura}_")
            with open(xml_firmado_path, "wb") as f:
                f.write(xml_firmado)

            chk = debug_verificar_referencias(xml_firmado)
            print("DEBUG DIGESTS:", chk)
            diag = verificar_firma_local(xml_firmado)
            print("VERIF_FIRMA_LOCAL:", diag)


            # 4) Enviar a SRI (Recepción + Autorización)
            xml_aut_path = None                  # ruta en disco del XML autorizado (si lo guarda)
            xml_autorizado_str = None
            
            resultado_sri = enviar_a_sri_y_autorizar(xml_firmado, clave_acceso)

            if not resultado_sri.get("ok"):
                # LOG & opcional: notificación interna
                print("SRI NO OK:", resultado_sri)
                # Puedes retornar HTTP 400 con detalle si deseas:
                # return JsonResponse({"ok": False, "sri": resultado_sri}, status=400)
            else:
                #print("SRI AUTORIZADO:", resultado_sri)  # 👈 solo para ver estado, número y XML
                # AUTORIZADO: añade datos al context (para tu PDF si quieres reemitir)
                context["claveAcceso"] = clave_acceso
                context["numeroAutorizacion"] = resultado_sri.get("numero_autorizacion", "")
                context["fechaAutorizacion"] = resultado_sri.get("fecha_autorizacion", "")
                
                xml_autorizado_str = resultado_sri.get("xml_autorizado", "")

                # Guarda XML autorizado a disco para adjuntar
                xml_aut_path = tempfile.mktemp(suffix=".xml", prefix=f"FAC_AUT_{numero_factura}_")
                with open(xml_aut_path, "wb") as f:
                    f.write(resultado_sri["xml_autorizado"].encode("utf-8"))

                # Opcional: genera barcode de la claveAcceso para incrustarlo en el PDF HTML
                try:
                    buf = io.BytesIO()
                    Code128(clave_acceso, writer=ImageWriter()).write(buf)
                    context["claveAccesoBarcodeBase64"] = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
                except Exception:
                    pass
            
                # (Opcional) si quieres regenerar el PDF con los datos de autorización y código de barras:
                # html_content = render_to_string('reciboPagoPdf.html', context)
                # HTML(string=html_content).write_pdf(pdf_path)
            #========FINALIZA SRI============#
            

            # === ENVÍO DE CORREO ===
            destinatario = email  # la dirección del cliente
            asunto = f'Factura electrónica #{numero_factura} – PC Computers'
            cuerpo = (
                'Estimado/a,\n\n'
                'Adjuntamos su factura electrónica:\n'
                ' - Factura.pdf: representación impresa.\n'
                ' - Factura.xml: documento oficial firmado digitalmente.\n'
                ' - (Si aplica) Factura_AUT.xml: XML autorizado por el SRI.\n\n'
                'Saludos cordiales,\nPC Computers'
            )

            mensaje = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                to=[destinatario],
            )

            # Adjuntar PDF (verifique que exista)
            if output_path and os.path.exists(output_path):
                with open(output_path, 'rb') as f_pdf:
                    mensaje.attach(
                        filename=f"Factura_{numero_factura}.pdf",
                        content=f_pdf.read(),
                        mimetype='application/pdf'
                    )
            else:
                print("WARN: output_path no existe o es None; no se adjunta PDF:", output_path)

            # Adjuntar XML firmado (siempre que exista)
            if xml_firmado_path and os.path.exists(xml_firmado_path):
                with open(xml_firmado_path, "rb") as f_xml:
                    mensaje.attach(
                        filename=f"Factura_{numero_factura}.xml",
                        content=f_xml.read(),
                        mimetype='application/xml'
                    )
            else:
                print("WARN: xml_firmado_path no existe o es None:", xml_firmado_path)

            # Adjuntar XML autorizado:
            # 1) Prioridad: si lo tengo en memoria, lo adjunto directo
            if xml_autorizado_str:
                mensaje.attach(
                    filename=f"Factura_AUT_{numero_factura}.xml",
                    content=xml_autorizado_str.encode("utf-8"),
                    mimetype='application/xml'
                )
            # 2) Alternativa: si lo guardé a disco y la ruta es válida
            elif xml_aut_path and os.path.exists(xml_aut_path):
                with open(xml_aut_path, "rb") as f_xml_aut:
                    mensaje.attach(
                        filename=f"Factura_AUT_{numero_factura}.xml",
                        content=f_xml_aut.read(),
                        mimetype='application/xml'
                    )
            else:
                print("INFO: No hay XML autorizado para adjuntar (aún).")

        # 1) Lanzar el envío de correo en segundo plano
        try:
            threading.Thread(
                target=enviar_correo_async,
                args=(mensaje, destinatario),
                daemon=True,  # el hilo no bloquea el cierre del proceso
            ).start()
        except Exception as e:
            print("Error al lanzar el hilo de envío de correo:", e)

        # 2) Bajar el stock SIEMPRE (independiente de que el correo se envíe o no)
        try:
            for prod in productos_a_facturar:
                codigo_producto = prod['codigo']
                cantidad_producto = prod['cantidad']
                try:
                    producto_stock = ColorStock.objects.get(id=codigo_producto)
                    nuevo_stock = int(producto_stock.stock) - int(cantidad_producto)
                    producto_stock.stock = nuevo_stock
                    producto_stock.save()
                except ColorStock.DoesNotExist:
                    print('debo bajar el stock mediante id y color')

            print("Proceso de stock ejecutado. Correo lanzado en segundo plano a:", destinatario)
        except Exception as e:
            print("Error al actualizar el stock:", e)
        
        
        
        # Realizar la consulta para obtener el usuario con el número de cédula dado
        try:
            usuario_adicional = adicionalUsuario.objects.get(cedula=cedula)
            # Si se encuentra un usuario con el número de cédula dado, 'usuario' contendrá ese objeto adicionalUsuario
            usuario_adicional.direccion = direccion
            usuario_adicional.direccionEnvio = direccionEnvio
            usuario_adicional.celular = celular
            usuario_adicional.ciudad = ciudad
            if (tipoVenta == 'Crédito')or (tipoVenta == 'Apartado'):
                    usuario_adicional.deuda = 'si'
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
            if (tipoVenta == 'Crédito') or (tipoVenta == 'Apartado'):
                    adicionalU.deuda = 'si'
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
                #user_id = request.user.id
                #nuevoRegistro.vendedor_id = user_id
                nuevoRegistro.vendedor_id = usuario_vendedor_completo.id
                nuevoRegistro.tipo_pago = tipoPago
                nuevoRegistro.tipo_venta = tipoVenta
                if (tipoVenta == 'Crédito')or (tipoVenta == 'Apartado'):
                    nuevoRegistro.deuda = 'si'
                    if abono:
                        nuevoRegistro.adelanto = abono
                    else:
                        nuevoRegistro.adelanto = 0
                nuevoRegistro.numero_factura = numero_factura
                nuevoRegistro.save()
                
                if tipoPago == 'Combinado':
                    if combinados_json:
                        pagoRegistroCombinado = PagoRegistroCombinado()
                        pagoRegistroCombinado.registro = nuevoRegistro
                        for item in combinados_json:
                            tipo = item.get('tipo')
                            valor = Decimal(item.get('valor'))
                            if tipo == 'Efectivo':
                                pagoRegistroCombinado.valorEfectivo = valor
                            if tipo == 'Tarjeta de Crédito':
                                pagoRegistroCombinado.valorTarjetaCredito = valor
                            if tipo == 'Cheque':
                                pagoRegistroCombinado.valorCheque = valor
                            if tipo == 'Transferencia':
                                pagoRegistroCombinado.valorTransferencia = valor
                            if tipo =='Tarjeta de Débito':
                                pagoRegistroCombinado.valorTarjetaDebito = valor
                        pagoRegistroCombinado.save()
                    
                    
                    
                
        except Exception as e:
            # Imprime la excepción para conocer el tipo y los detalles del error
            print("Error al guardar el registro:", e)
        
        try:
            if (tipoVenta == 'Crédito')or (tipoVenta == 'Apartado'):
                 
                deudaPendiente = Decimal(total) - Decimal(nuevoRegistro.adelanto) 
                    
                #try:
                #    deuda = Deudas.objects.get(usuario=usuario)
                #    deuda.total = Decimal(deuda.total) + total
                #    deuda.saldo = Decimal(deuda.saldo) + deudaPendiente
                #except Deudas.DoesNotExist:  
                #    deuda = Deudas()
                #    deuda.total = total
                #    deuda.saldo = deudaPendiente
                deuda = Deudas()
                deuda.total = total
                deuda.saldo = deudaPendiente
                deuda.usuario = usuario
                deuda.registro= nuevoRegistro
                deuda.save()
                
                # Iterar sobre los productos para convertirlos a float y guardarlos
                for producto in productos_fac:
                    # Convertir el campo 'precio' de Decimal a float
                    producto['precio'] = float(producto['precio'])
                    # Convertir el campo 'preciot' de Decimal a float
                    producto['preciot'] = float(producto['preciot'])
                
                #GUARDAR DATOS DE LA FACTURA PARA LUEGO IMPRIMIRLA
                facturaCredito=FacturaCredito()
                facturaCredito.deuda=deuda
                facturaCredito.nombre=nombre
                facturaCredito.apellidos=apellidos
                facturaCredito.cedula=cedula
                facturaCredito.email=email
                facturaCredito.celular=celular
                facturaCredito.ciudad=ciudad
                facturaCredito.direccion=direccion
                facturaCredito.direccionEnvio=direccionEnvio
                facturaCredito.productos=productos_fac
                facturaCredito.subtotal=subtotal
                facturaCredito.porcentaje=porcentaje
                facturaCredito.descuento=descuento
                facturaCredito.subtotalD=subtotalD
                facturaCredito.porcentajeDescuento=porcentajeDescuento
                facturaCredito.iva=iva
                facturaCredito.total=total
                facturaCredito.tipoPago=tipoPago
                facturaCredito.peso=peso
                facturaCredito.fecha=fecha_hora_actual
                facturaCredito.numeroCheque=numeroCheque
                facturaCredito.numeroFactura=numero_factura
                facturaCredito.combinados=combinados_json
                facturaCredito.tipoVenta=tipoVenta
                facturaCredito.abono=abono
                facturaCredito.saldo=saldo
                facturaCredito.usuarioVendedor=usuarioVendedor
                facturaCredito.save()
                
        except Exception as e:
            # Imprime la excepción para conocer el tipo y los detalles del error
            print("Error al guardar deudas:", e)
        
        #######REEMPLACE ESTE CODIGO PARA MEJORAR LA DESCARGA, SI EXISTE ERROR BORRAR##########
        # Seguridad: verificar que el archivo exista y tenga contenido
        if not os.path.exists(output_path):
            raise Http404("No se encontró el PDF generado.")

       # Leer el PDF generado
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()  # ✅ contenido real del PDF
            
        if not pdf_bytes:
            raise Http404("El PDF está vacío.")

        # Codificar a base64 directamente (sin usar BytesIO)
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # (Opcional) eliminar archivo temporal
        
        # Guardar los detalles de la factura
        factura = FacturaCompleta.objects.create(
            numero_factura=numero_factura,
            cliente=usuario_adicional.user,
            total=total,
            descuento=descuento,
            estado='Pendiente'  # Estado inicial de la factura
        )

        # Guardar el XML de la factura
        factura_xml = FacturaXML.objects.create(
            factura=factura,
            xml_content=xml_firmado_path,  # El contenido del XML generado
            xml_firmado=xml_firmado,  # El XML firmado
            estado_autorizacion='Pendiente',  # O el estado que corresponda
        )

        if resultado_sri.get("ok"):
            # Actualizar el estado del XML autorizado
            factura_xml.estado_autorizacion = 'AUTORIZADO'
            factura_xml.numero_autorizacion = resultado_sri.get("numero_autorizacion", "")
            factura_xml.fecha_autorizacion = resultado_sri.get("fecha_autorizacion", "")
            factura_xml.save()

            factura.estado = 'Pagada'  # Cambiar el estado de la factura si corresponde
            factura.save()

        
        try:
            os.remove(output_path)
        except OSError:
            pass  # no bloquear por esto

        log = logging.getLogger(__name__)

        # ...
        log.warning("RENDER_DESCARGA -> num_factura=%s", numero_factura)

        # Renderizar el template
        # Renderizar la página que dispara la descarga y luego redirige
        return render(request, "descargar_pdf_facturacion.html", {
            "encoded_pdf": encoded_pdf,                 # en el template usa |escapejs
            "download_filename": f"Factura_{numero_factura}.pdf",
            "redirect_url": "/ventas/",      # cambia si quieres
        })
        ################### HASTA AQUI, LO QUE ESTA A CONTINUACION ES EL CODIGO ANTERIOR##########
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
    
@login_required
@vendedor_required
def pago_pendiente(request):
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        vendedor = User.objects.get(username=request.user)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        try:
            clientes = User.objects.all()
        except adicionalUsuario.DoesNotExist:
            clientes=''
            
        try:
            # Usando select_related para obtener los datos adicionales de cada usuario
            usuarios = adicionalUsuario.objects.select_related('user').all()
        except adicionalUsuario.DoesNotExist:
            usuarios = ''
        
        # Crear una lista para almacenar los datos combinados de usuarios y sus datos adicionales
        usuarios_con_datos_adicionales = []

        for usuario_adicional in usuarios:
            usuario = usuario_adicional.user
            if usuario:  # Verificar si el usuario existe
                datos_adicionales = {
                    'id':usuario.id,
                    'nombre': usuario.first_name +' '+usuario.last_name,
                    'cedula': usuario_adicional.cedula,
                    # Agrega más campos de ser necesario
                }
                usuarios_con_datos_adicionales.append(datos_adicionales)
        
        #print(usuarios_con_datos_adicionales)
        clientes_json = json.dumps(usuarios_con_datos_adicionales)
        
        return render(request, 'ventas_pagopendiente.html', {"caja":caja,"clientes":clientes_json})
    except Caja.DoesNotExist:
        return render(request, 'ventas_inicio.html',{})

def devolver_abono(request):
    # Usando select_related para obtener los datos adicionales de cada usuario
    vendedor = User.objects.get(username=request.user)
    caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
    if request.method == 'POST':
        valor = request.POST.get('valor')
        datos = request.POST.get('datos')
        
        nuevo_gasto = Gasto(
                    valor=Decimal(valor),
                    descripcion="Devolución de abono anticipado por servicio cancelado de " + datos,
                    caja = caja,
                    usuario = request.user
                )
        nuevo_gasto.save()
        
        # Aquí puedes procesar los datos, como guardarlos en la base de datos
        # Por ejemplo:
        # Abono.objects.create(valor=valor, datos=datos)

        # Retornar una respuesta JSON
        return JsonResponse({'status': 'success', 'message': 'Abono procesado correctamente.'})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

def buscar_deuda(request): 
    cedula = request.GET.get('cedula')
    usuario = get_object_or_404(adicionalUsuario, cedula=cedula)
    usuario_completo = usuario.user
    
    
    try:
        todosRegistros = Registro.objects.filter(usuario=usuario_completo, deuda='si')
        todosRegistros = [model_to_dict(registro) for registro in todosRegistros]
        
    except Registro.DoesNotExist:
        todosRegistros = []
        
    try:
        registrosPagos = Pago.objects.filter(usuario=usuario_completo, estado='pendiente')
        registrosPagos = [{**model_to_dict(pagos),'numero_factura': pagos.deuda.registro.numero_factura} 
                          for pagos in registrosPagos
        ]
        
    except Registro.DoesNotExist:
        registrosPagos = []
    
    try:
        totalD = 0
        totalS = 0
        detalleDeuda = Deudas.objects.filter(usuario=usuario_completo, estado='pendiente')
        for d in detalleDeuda:
            totalD = totalD + d.total 
            totalS = totalS + d.saldo
            
            
        #detalleDeuda = [model_to_dict(deuda) for deuda in detalleDeuda]
        detalleDeuda = [
            {**model_to_dict(d), 'numero_factura': d.registro.numero_factura}
            for d in detalleDeuda
        ]
        
        print(detalleDeuda)
        # Realiza las operaciones necesarias con el producto obtenido
        data = {
        'deuda':usuario.deuda,
        'nombre': usuario_completo.first_name,
        'apellido': usuario_completo.last_name,
        'cedula':usuario.cedula,
        'email':usuario_completo.email,
        'total':totalD,
        'saldo':totalS,
        'detalleDeuda':detalleDeuda,
        'todosRegistros':todosRegistros,
        'registrosPagos':registrosPagos
        # Agrega aquí más datos del cliente que desees devolver
        }
    except Deudas.DoesNotExist:
        data = {
            'deuda':usuario.deuda,
            'nombre': usuario_completo.first_name,
            'apellido': usuario_completo.last_name,
            'todosRegistros':todosRegistros,
            'registrosPagos':registrosPagos
            # Agrega aquí más datos del cliente que desees devolver
        }
        
    return JsonResponse(data)

def agregarPago(request):
    if request.method == 'POST':
        # Obtener el valor del campo 'pago' del formulario
        pago = request.POST.get('pago')
        # Obtener el valor del campo 'otroCampo' del formulario
        cedula = request.POST.get('cedula')
        idDeuda = request.POST.get('idDeuda')
        t = request.POST.get('total')
        tipoPago = request.POST.get('tipoPago')
        # Realizar acciones con los datos recibidos, como almacenarlos en una base de datos, procesarlos, etc.
        fecha_hora_actual = dj_timezone.now()
        
        if (tipoPago == 'Combinado'):
            totalCombinado = 0
            inputEfectivo = request.POST.get('efectivo')
            if inputEfectivo:
                totalCombinado = totalCombinado + Decimal(inputEfectivo)
            inputtCredito = request.POST.get('tCredito')
            if inputtCredito:
                totalCombinado = totalCombinado + Decimal(inputtCredito)
            inputCheque = request.POST.get('cheque')
            if inputCheque:
                totalCombinado = totalCombinado + Decimal(inputCheque)
            inputTransferencia = request.POST.get('transferencia')
            if inputTransferencia:
                totalCombinado = totalCombinado + Decimal(inputTransferencia)
            inputtDebito = request.POST.get('tDebito')
            if inputtDebito:
                totalCombinado = totalCombinado + Decimal(inputtDebito)
            pago = totalCombinado
        
        
        try:
            usuario = adicionalUsuario.objects.get(cedula=cedula)
            
        except adicionalUsuario.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado, intente nuevamente.'}, status=400)
        
        try:
            detalleDeuda = Deudas.objects.get(id=idDeuda)
            # Realiza las operaciones necesarias con el producto obtenido
        except Deudas.DoesNotExist:
            return JsonResponse({'error': 'Deuda no encontrada, intente nuevamente.'}, status=400)
        
        try:
            todosPagos = Pago.objects.filter(usuario=usuario.user, estado='pendiente')
            # Realiza las operaciones necesarias con el producto obtenido
        except Deudas.DoesNotExist:
            todosPagos = ""
        
        saldo = Decimal(detalleDeuda.saldo) - Decimal(pago)
        
        context = {
            'nombre':usuario.user.first_name,
            'apellidos':usuario.user.last_name,
            'cedula':cedula,
            'email':usuario.user.email,
            'celular':usuario.celular,
            'ciudad':usuario.ciudad,
            'direccion':usuario.direccion,
            'fecha':fecha_hora_actual,
            'abono':pago,
            'primer_pago':detalleDeuda.registro.adelanto,
            'primer_pago_fecha':detalleDeuda.registro.fecha_hora,
            'saldo':saldo,
            'usuarioVendedor':request.user,
            'total':detalleDeuda.total,
            'transaccion':detalleDeuda.id,
            'todosPagos':todosPagos,
            'numeroFactura':detalleDeuda.registro.numero_factura,
            'aux':'1'
        }
        
        ###         PARA WHTMLTOPDF
        #html_content = render_to_string('ventas_recibopagocredito.html', context)

        # Guardar el contenido HTML en un archivo temporal
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
        #    temp_html.write(html_content.encode('utf-8'))
        #    temp_html_path = temp_html.name

        # Configuración de pdfkit
        #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        
        # Personalizar el nombre del archivo PDF
        # Personalizar el nombre del archivo PDF
        #nombre_archivo_pdf = 'ReciboPago_{}_{}_{}.pdf'

        # Convertir el archivo HTML temporal a PDF
        #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=nombre_archivo_pdf).name
        #pdfkit.from_file(temp_html_path, output_path, configuration=config)

        #### PARA WEASYPRINT
        # Generar PDF y enviar
        html_content = render_to_string('ventas_recibopagocredito.html', context)

        # Convertir directamente a PDF usando WeasyPrint
        #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
        output_path = tempfile.mktemp(suffix='.pdf')  
        HTML(string=html_content).write_pdf(output_path)
            

        # Codificar la ruta
        encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                

        #enviar por correo el pdf
        destinatario = usuario.user.email  # O la dirección de correo electrónico a la que deseas enviar el correo
        asunto = 'Facturacion emitida por PC Computers'
        cuerpo = 'Adjunto encontrarás la factura emitida por PC Computers.'
        archivo_adjunto = output_path
        # Crear mensaje de correo electrónico
        mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
        # Adjuntar archivo PDF
        archivo_adjunto = open(archivo_adjunto, 'rb')
        mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
        archivo_adjunto.close()
        # Enviar correo electrónico
        try:
            
            with transaction.atomic():
                nuevoPago = Pago()
                nuevoPago.usuario = usuario.user
                nuevoPago.deuda = detalleDeuda
                nuevoPago.fecha_hora = fecha_hora_actual
                nuevoPago.cuota = Decimal(pago)
                nuevoPago.tipoPago = tipoPago
                if tipoPago == 'Transferencia':
                    ntransferencia = request.POST.get('ntransferencia')
                    nuevoPago.numeroTransferencia =ntransferencia
                if tipoPago == 'Cheque':
                    ncheque = request.POST.get('ncheque')
                    banco = request.POST.get('banco')
                    nuevoPago.numeroCheque = ncheque
                    nuevoPago.banco = banco
                nuevoPago.save()
                
                if tipoPago == 'Combinado':
                    pagoCombinado = PagoPendienteCombinado()
                    pagoCombinado.pago = nuevoPago
                    efectivo = request.POST.get('efectivo')
                    if efectivo:
                        pagoCombinado.valorEfectivo = efectivo
                    tCredito = request.POST.get('tCredito')
                    if tCredito:
                        pagoCombinado.valorTarjetaCredito = tCredito
                    cheque = request.POST.get('cheque')
                    if cheque:
                        pagoCombinado.valorCheque = cheque
                    transferencia = request.POST.get('transferencia')
                    if transferencia:
                        pagoCombinado.valorTransferencia = transferencia
                    tDebito = request.POST.get('tDebito')
                    if tDebito:
                        pagoCombinado.valorTarjetaDebito = tDebito
                    pagoCombinado.save()
            
            deuda = Deudas.objects.get(id=idDeuda)
            deudaSaldo = Decimal(deuda.saldo) - Decimal(pago)
            
            if deudaSaldo <= 0:
                # El código aquí se ejecutará si deudaSaldo es menor o igual a 0.
                print("El saldo es menor o igual a cero.")
                
                pagos = Pago.objects.filter(deuda=detalleDeuda)
                for p in pagos:
                    p.estado = 'terminado'
                    p.save()
                    
                #registro = Registro.objects.get(usuario=usuario.user, total_vendido=t, deuda='si')
                #for r in registros:
                registro = deuda.registro
                registro.deuda = 'no'
                registro.save()
                
                todosRegistros = Registro.objects.filter(usuario=usuario.user)
                tienedeuda = 'no'
                for tr in todosRegistros:
                    if tr.deuda == 'si':
                        tienedeuda= 'si'
                
                adicionalUsua = adicionalUsuario.objects.get(user = usuario.user)
                adicionalUsua.deuda = tienedeuda
                adicionalUsua.save()
                
                deuda.total = 0
                deuda.saldo = 0
                deuda.estado = 'pagada'
                deuda.save()
                
                #obtener la factura para imprimirla
                facturaCredito = FacturaCredito.objects.get(deuda=detalleDeuda)
                
                
                # Obtener la cadena JSON de productos
                #productos_json_str = facturaCredito.productos

                # Convertir la cadena JSON a un objeto Python
                #productos = json.loads(productos_json_str)
                
                # Convertir la cadena de texto en un objeto de fecha y hora
                fecha_objeto = datetime.strptime(facturaCredito.fecha, '%Y-%m-%d %H:%M:%S.%f%z')

                # Convierte la fecha original a la zona horaria configurada en tus settings
                fecha_con_zona = dj_timezone.localtime(fecha_objeto)

                # Formatea la fecha y hora para mostrarlas en la plantilla
                fecha_formateada = fecha_con_zona.strftime('%d/%m/%Y %H:%M:%S')
                
                context = {
                    'nombre':facturaCredito.nombre,
                    'apellidos':facturaCredito.apellidos,
                    'cedula':facturaCredito.cedula,
                    'email':facturaCredito.email,
                    'celular':facturaCredito.celular,
                    'ciudad':facturaCredito.ciudad,
                    'direccion':facturaCredito.direccion,
                    'direccionEnvio':facturaCredito.direccionEnvio,
                    'productos': facturaCredito.productos,
                    'subtotal':facturaCredito.subtotal,
                    'porcentaje':facturaCredito.porcentaje,
                    'descuento':facturaCredito.descuento,
                    'subtotalD':facturaCredito.subtotalD,
                    'porcentajeDescuento':facturaCredito.porcentajeDescuento,
                    'iva':facturaCredito.iva,
                    'total':facturaCredito.total,
                    'tipoPago':facturaCredito.tipoPago,
                    'peso':facturaCredito.peso,
                    'fecha':fecha_formateada,
                    'numeroCheque':facturaCredito.numeroCheque,
                    'numeroFactura':facturaCredito.numeroFactura,
                    'combinados':facturaCredito.combinados,
                    'tipoVenta':facturaCredito.tipoVenta,
                    'abono':facturaCredito.abono,
                    'saldo':'0.00',
                    'usuarioVendedor':facturaCredito.usuarioVendedor
                }
                print(context)
                
                ###         PARA WHTMLTOPDF
                #html_content = render_to_string('reciboPagoPdf.html', context)

                # Guardar el contenido HTML en un archivo temporal
                #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
                #    temp_html.write(html_content.encode('utf-8'))
                #    temp_html_path = temp_html.name

                # Configuración de pdfkit
                #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
                
                # Personalizar el nombre del archivo PDF
                # Personalizar el nombre del archivo PDF
                #nombre_archivo_pdf = 'ReciboPago_{}_{}_{}.pdf'

                # Convertir el archivo HTML temporal a PDF
                #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=nombre_archivo_pdf).name
                #pdfkit.from_file(temp_html_path, output_path, configuration=config)

                #### PARA WEASYPRINT
                # Generar PDF y enviar
                html_content = render_to_string('reciboPagoPdf.html', context)

                # Convertir directamente a PDF usando WeasyPrint
                #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
                output_path = tempfile.mktemp(suffix='.pdf')    
                HTML(string=html_content).write_pdf(output_path)
                    

                # Codificar la ruta
                encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                
                

                #enviar por correo el pdf
                destinatario = usuario.user.email  # O la dirección de correo electrónico a la que deseas enviar el correo
                asunto = 'Facturacion emitida por PC Computers'
                cuerpo = 'Adjunto encontrarás la factura emitida por PC Computers.'
                archivo_adjunto = output_path
                # Crear mensaje de correo electrónico
                mensaje = EmailMultiAlternatives(asunto, cuerpo, 'noreply@example.com', [destinatario])
                # Adjuntar archivo PDF
                archivo_adjunto = open(archivo_adjunto, 'rb')
                mensaje.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')
                archivo_adjunto.close()
                
            else:
                # El código aquí se ejecutará si deudaSaldo es mayor que 0.
                print("El saldo es mayor que cero.")
                deuda.saldo = deudaSaldo
                deuda.save()
            
            # Envía el correo electrónico
            mensaje.send()
           
            print("Correo electrónico enviado correctamente a:", destinatario)
        except ValidationError as e:
            print("Error de validación al enviar el correo electrónico:", e)
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
    
        # Leer el contenido del PDF y codificarlo en base64
        with open(output_path, 'rb') as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')

        return JsonResponse({'pdf_base64': pdf_base64, 'filename': 'Recibo_de_Pago.pdf'})
        
    return render(request, 'ventas_recibopagocredito.html')

@vendedor_required
def ventas_caja(request):
    # Usando select_related para obtener los datos adicionales de cada usuario
    vendedor = User.objects.get(username=request.user)
    caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
    
    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now()
    # Formatear la fecha y hora si es necesario
    fecha_hora = fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    
    return render(request, 'ventas_comprobar_caja.html',{'caja':caja,'fecha':fecha_hora})


@vendedor_required
def comprobar_ventas_caja(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        efectivoContado = data.get('efectivo', None)
        cajero_username = data.get('cajero', None)
        vendedor = User.objects.get(username=cajero_username)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        
        # Aquí puedes procesar los datos como necesites
        #caja = Caja.objects.latest('fecha_hora_inicio')
        
        # Obtener la fecha y hora de inicio de la caja
        fecha_inicio = caja.fecha_hora_inicio
        
        # Obtener la fecha y hora actual
        fecha_actual = dj_timezone.now()
        
        # Filtrar los registros que están dentro del rango de fecha desde fecha_inicio hasta fecha_actual
        registros = Registro.objects.filter(fecha_hora__range=(fecha_inicio, fecha_actual))
        pagosRegistros = Pago.objects.filter(fecha_hora__range=(fecha_inicio, fecha_actual))

        fondoCaja = Decimal(caja.valor_apertura)
        
        totalVendido = 0
        transferencias_ventas = 0
        cheques_ventas = 0
        tarjetas_ventas = 0
        
        for r in registros:
            if r.tipo_venta == 'Contado':
                if r.tipo_pago == 'Efectivo':
                    totalVendido = totalVendido + Decimal(r.total_vendido)
                if r.tipo_pago == 'Transferencia':
                    transferencias_ventas = transferencias_ventas + Decimal(r.total_vendido)
                if r.tipo_pago == 'Tarjeta de Crédito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.total_vendido)
                if r.tipo_pago == 'Tarjeta de Débito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.total_vendido)
                if r.tipo_pago == 'Cheque':
                    cheques_ventas = cheques_ventas + Decimal(r.total_vendido)
                if r.tipo_pago == 'Combinado':
                    try:
                        pagoRegistroCombinado = PagoRegistroCombinado.objects.get(registro = r)
                        if pagoRegistroCombinado.valorEfectivo:
                            totalVendido = totalVendido + Decimal(pagoRegistroCombinado.valorEfectivo)
                        if pagoRegistroCombinado.valorTarjetaCredito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaCredito)
                        if pagoRegistroCombinado.valorTarjetaDebito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaDebito)
                        if pagoRegistroCombinado.valorCheque:
                            cheques_ventas = cheques_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                        if pagoRegistroCombinado.valorTransferencia:
                            transferencias_ventas = transferencias_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                    except PagoServicioCombinado.DoesNotExist:
                        pagoRegistroCombinado = ''
            if r.tipo_venta == 'Crédito':
                if r.tipo_pago == 'Efectivo':
                    totalVendido = totalVendido + Decimal(r.adelanto)
                if r.tipo_pago == 'Transferencia':
                    transferencias_ventas = transferencias_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Tarjeta de Crédito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Tarjeta de Débito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Cheque':
                    cheques_ventas = cheques_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Combinado':
                    try:
                        pagoRegistroCombinado = PagoRegistroCombinado.objects.get(registro = r)
                        if pagoRegistroCombinado.valorEfectivo:
                            totalVendido = totalVendido + Decimal(pagoRegistroCombinado.valorEfectivo)
                        if pagoRegistroCombinado.valorTarjetaCredito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaCredito)
                        if pagoRegistroCombinado.valorTarjetaDebito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaDebito)
                        if pagoRegistroCombinado.valorCheque:
                            cheques_ventas = cheques_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                        if pagoRegistroCombinado.valorTransferencia:
                            transferencias_ventas = transferencias_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                    except PagoServicioCombinado.DoesNotExist:
                        pagoRegistroCombinado = ''
            if r.tipo_venta == 'Apartado':
                if r.tipo_pago == 'Efectivo':
                    totalVendido = totalVendido + Decimal(r.adelanto)
                if r.tipo_pago == 'Transferencia':
                    transferencias_ventas = transferencias_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Tarjeta de Crédito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.adelanto)
                    tarjetas_credito_ventas = tarjetas_credito_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Tarjeta de Débito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(r.adelanto)
                    tarjetas_debito_ventas = tarjetas_debito_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Cheque':
                    cheques_ventas = cheques_ventas + Decimal(r.adelanto)
                if r.tipo_pago == 'Combinado':
                    try:
                        pagoRegistroCombinado = PagoRegistroCombinado.objects.get(registro = r)
                        if pagoRegistroCombinado.valorEfectivo:
                            totalVendido = totalVendido + Decimal(pagoRegistroCombinado.valorEfectivo)
                        if pagoRegistroCombinado.valorTarjetaCredito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaCredito)
                            tarjetas_credito_ventas = tarjetas_credito_ventas + Decimal(pagoRegistroCombinado.valorTarjetaCredito)
                        if pagoRegistroCombinado.valorTarjetaDebito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoRegistroCombinado.valorTarjetaDebito)
                            tarjetas_debito_ventas = tarjetas_debito_ventas + Decimal(pagoRegistroCombinado.valorTarjetaDebito)
                        if pagoRegistroCombinado.valorCheque:
                            cheques_ventas = cheques_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                        if pagoRegistroCombinado.valorTransferencia:
                            transferencias_ventas = transferencias_ventas + Decimal(pagoRegistroCombinado.valorCheque)
                    except PagoServicioCombinado.DoesNotExist:
                        pagoRegistroCombinado = ''
            
                
        for pr in pagosRegistros:
            if pr.tipoPago == 'Efectivo':
                totalVendido = totalVendido + Decimal(pr.cuota)
            if pr.tipoPago == 'Transferencia':
                transferencias_ventas = transferencias_ventas + Decimal(pr.cuota)
            if pr.tipoPago == 'Tarjeta de Crédito':
                tarjetas_ventas = tarjetas_ventas + Decimal(pr.cuota)
            if pr.tipoPago == 'Tarjeta de Débito':
                tarjetas_ventas = tarjetas_ventas + Decimal(pr.cuota)
            if pr.tipoPago == 'Cheque':
                cheques_ventas = cheques_ventas + Decimal(pr.cuota)
            if pr.tipoPago == 'Combinado':
                try:
                    pagoPendienteCombinado = PagoPendienteCombinado.objects.get(pago = pr)
                    if pagoPendienteCombinado.valorEfectivo:
                        totalVendido = totalVendido + Decimal(pagoPendienteCombinado.valorEfectivo)
                    if pagoPendienteCombinado.valorTarjetaCredito:
                        tarjetas_ventas = tarjetas_ventas + Decimal(pagoPendienteCombinado.valorTarjetaCredito)
                    if pagoPendienteCombinado.valorTarjetaDebito:
                        tarjetas_ventas = tarjetas_ventas + Decimal(pagoPendienteCombinado.valorTarjetaDebito)
                    if pagoPendienteCombinado.valorCheque:
                        cheques_ventas = cheques_ventas + Decimal(pagoPendienteCombinado.valorCheque)
                    if pagoPendienteCombinado.valorTransferencia:
                        transferencias_ventas = transferencias_ventas + Decimal(pagoPendienteCombinado.valorCheque)
                except PagoPendienteCombinado.DoesNotExist:
                    pagoPendienteCombinado = ''
            
        totalEgresos = Decimal(0)
        try:
            egresos = Gasto.objects.filter(caja = caja)
            for e in egresos:
                totalEgresos = totalEgresos + Decimal(e.valor)
        except Gasto.DoesNotExist:
            totalEgresos = Decimal(0)
            
        totalIngresos = Decimal(0)
        try:
            ingresos = Ingreso.objects.filter(caja = caja)
            for i in ingresos:
                totalIngresos = totalIngresos + Decimal(i.valor)
        except Ingreso.DoesNotExist:
            totalIngresos = Decimal(0)
            
        total_servicios = 0
        transferencias_servicios = 0
        cheques_servicios = 0
        tarjetas_servicios = 0  
        try:
            pagoservicios = PagoServicio.objects.filter(caja = caja)
            for s in pagoservicios:
                if s.tipoPago == 'Efectivo':
                    total_servicios = total_servicios + Decimal(s.abono)
                    
                if s.tipoPago == 'Transferencia':
                    transferencias_servicios = transferencias_servicios + Decimal(s.abono)
                if s.tipoPago == 'Cheque':
                    cheques_servicios = cheques_servicios + Decimal(s.abono)
                if s.tipoPago == 'Tarjeta de Crédito':
                    tarjetas_servicios = tarjetas_servicios + Decimal(s.abono)
                if s.tipoPago == 'Tarjeta de Débito':
                    tarjetas_servicios = tarjetas_servicios + Decimal(s.abono)
                if s.tipoPago == 'Combinado':
                    try:
                        pagoCombinado = PagoServicioCombinado.objects.get(pagoServicio = s)
                        if pagoCombinado.valorEfectivo:
                            total_servicios = total_servicios + Decimal(pagoCombinado.valorEfectivo)
                        if pagoCombinado.valorTarjetaCredito:
                            tarjetas_servicios = tarjetas_servicios + Decimal(pagoCombinado.valorTarjetaCredito)
                        if pagoCombinado.valorTarjetaDebito:
                            tarjetas_servicios = tarjetas_servicios + Decimal(pagoCombinado.valorTarjetaDebito)
                        if pagoCombinado.valorCheque:
                            cheques_servicios = cheques_servicios + Decimal(pagoCombinado.valorCheque)
                        if pagoCombinado.valorTransferencia:
                            transferencias_servicios = transferencias_servicios + Decimal(pagoCombinado.valorTransferencia)
                    except PagoServicioCombinado.DoesNotExist:
                        pagoCombinado = ''
        except PagoServicio.DoesNotExist:
            total_servicios = Decimal(0)
        
        totalEfectivo = fondoCaja + totalVendido + total_servicios + totalIngresos - totalEgresos

        sobrante = Decimal('0')
        faltante = Decimal('0')

        #compruebo que el total efectivo no sea negativo
        if totalEfectivo > 0:
            diferencia = Decimal(totalEfectivo) - Decimal(efectivoContado)
            # Determinar el sobrante o el faltante basado en la diferencia
            if diferencia < 0:
                sobrante = abs(diferencia)
            elif diferencia > 0:
                faltante = abs(diferencia)
        else:
            diferencia = Decimal(totalEfectivo) + Decimal(efectivoContado)
            # Determinar el sobrante o el faltante basado en la diferencia
            if diferencia > 0:
                sobrante = abs(diferencia)
            elif diferencia < 0:
                faltante = abs(diferencia)
        
        totalCheques = cheques_ventas + cheques_servicios
        totalTransferencias = transferencias_servicios + transferencias_ventas
        totalTarjetas = tarjetas_servicios + tarjetas_ventas
        
        # Devuelve una respuesta JSON
        response_data = {
            'message': 'Datos recibidos correctamente',
            'fondoCaja':fondoCaja,
            'totalVendido':totalVendido,
            'totalServicios':total_servicios,
            'totalEgresos':totalEgresos,
            'totalIngresos':totalIngresos,
            'totalEfectivo':totalEfectivo,
            'chequesServicios':cheques_servicios,
            'chequesVentas':cheques_ventas,
            'totalCheques':totalCheques,
            'transferenciasServicios':transferencias_servicios,
            'transferenciasVentas':transferencias_ventas,
            'totalTransferencias':totalTransferencias,
            'tarjetasServicios':tarjetas_servicios,
            'tarjetasVentas':tarjetas_ventas,
            'totalTarjetas':totalTarjetas,
            'efectivoContado': efectivoContado,
            'faltante':faltante,
            'sobrante':sobrante,
        }
        
        print(response_data)
        
        return JsonResponse(response_data)

    # Si la solicitud no es POST, devolver un error apropiado (en desarrollo, puede ser 405 Method Not Allowed)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@vendedor_required
def ventas_clientes(request):
    if request.method == 'POST':
        id = request.POST.get('id', '').strip()
        
        # Obtener datos del formulario
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        celular = request.POST.get('celular', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        direccion_envio = request.POST.get('direccionEnvio', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validaciones básicas
        errores = []
        if not nombres:
            errores.append("El campo 'Nombres' es obligatorio.")
        if not apellidos:
            errores.append("El campo 'Apellidos' es obligatorio.")
        if not id:
            # Validación de formato de identificación
            # Validación de formato + lógica completa (cédula / RUC)
            ok, msg = es_identificacion_valida_cedula_o_ruc(cedula)

            if not ok:
                # Mensaje técnico proveniente de la función, o uno genérico
                errores.append("La identificación ingresada no es válida.")
            # Validación de unicidad
            if adicionalUsuario.objects.filter(cedula=cedula).exists():
                errores.append("Ya existe un cliente con esa cédula/Ruc.")
            if User.objects.filter(email=correo).exists():
                errores.append("Ya existe un cliente con ese correo.")
        if not ciudad:
            errores.append("El campo 'Ciudad' es obligatorio.")
        if not direccion:
            errores.append("El campo 'Dirección' es obligatorio.")
        if not direccion_envio:
            errores.append("El campo 'Dirección de Envío' es obligatorio.")

        # Si hay errores, mostrar mensajes
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('vistaclientes')  # Asegúrate que este sea tu URL name
        
        
        if id:
            adicionalusuario = adicionalUsuario.objects.get(id = id)
            usuario = adicionalusuario.user
        else:
            usuario = User()
            adicionalusuario = adicionalUsuario()
            adicionalusuario.cedula = cedula
            usuario.username = cedula
        
        usuario.first_name = nombres
        usuario.last_name = apellidos
        usuario.email = correo
        usuario.save()
        
        adicionalusuario.celular = celular
        adicionalusuario.ciudad = ciudad
        adicionalusuario.direccion = direccion
        adicionalusuario.direccionEnvio = direccion_envio
        adicionalusuario.user = usuario
        adicionalusuario.save()
        
        if id:
            messages.success(request, "Usuario '"+nombres+" "+apellidos+"' editado exitosamente.")
        else:
            messages.success(request, "Usuario '"+nombres+" "+apellidos+"' creado exitosamente.")
    # Usuarios que NO tienen grupos ni permisos
    usuarios_sin_grupos_permisos = User.objects.filter(groups=None, user_permissions=None)

    # Traer los adicionalUsuario cuyo user esté en esa lista
    usuariosfiltrados = adicionalUsuario.objects.filter(user__in=usuarios_sin_grupos_permisos)
    
    return render(request, 'ventas_clientes.html',{"usuarios":usuariosfiltrados})

@vendedor_required
def actualizar_estado_servicio(request):
    servicio_id = request.POST.get('servicio_id')
    nuevo_estado = request.POST.get('nuevo_estado')
    
    if nuevo_estado == 'finalizar':
        return redirect('/ventas/registro_servicios/abono/'+servicio_id+'')

    servicio = Servicio.objects.get(id=servicio_id)
    estado_anterior = servicio.estado
    servicio.estado = nuevo_estado
    servicio.save()
    
    messages.success(
            request,
            f"El servicio #{servicio.id} cambió de '{estado_anterior}' a '{nuevo_estado}'."
        )

    return redirect('/ventas/servicio/todos_registros')

@vendedor_required
def editar_gasto(request):
    if request.method == "POST":
        gasto = Gasto.objects.get(id=request.POST["id"])
        gasto.valor = request.POST["valor"]
        gasto.descripcion = request.POST["descripcion"]
        gasto.save()
    return redirect("/ventas/gastos")

@vendedor_required
def eliminar_gasto(request):
    if request.method == "POST":
        Gasto.objects.filter(id=request.POST["id"]).delete()
    return redirect("/ventas/gastos")

@vendedor_required
def editar_ingreso(request):
    if request.method == "POST":
        ingreso_id = request.POST.get("id")
        valor = request.POST.get("valor")
        descripcion = request.POST.get("descripcion")

        ingreso = get_object_or_404(Ingreso, id=ingreso_id)
        ingreso.valor = valor
        ingreso.descripcion = descripcion
        ingreso.save()

    return redirect("/ventas/gastos")  # o tu ruta principal

@vendedor_required
def eliminar_ingreso(request):
    if request.method == "POST":
        ingreso_id = request.POST.get("id")
        ingreso = get_object_or_404(Ingreso, id=ingreso_id)
        ingreso.delete()

    return redirect("/ventas/gastos") 


def es_cedula_ec_valida(ident: str) -> bool:
    """
    Valida cédula ecuatoriana de persona natural (10 dígitos).
    Regla estándar: coeficientes 2,1,2,1,2,1,2,1,2 sobre los primeros 9 dígitos.
    """
    if len(ident) != 10 or not ident.isdigit():
        return False

    provincia = int(ident[0:2])
    tercer = int(ident[2])

    # Provincia válida (01–24) y 3er dígito < 6 para persona natural
    if not (1 <= provincia <= 24) or tercer >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        valor = int(ident[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9
        total += valor

    verificador_calculado = (10 - (total % 10)) % 10
    verificador_real = int(ident[9])

    return verificador_calculado == verificador_real


def es_ruc_persona_natural_valido(ident: str) -> bool:
    """
    Valida RUC de persona natural: 13 dígitos donde
    los primeros 10 forman una cédula válida y los últimos 3 son > 000.
    (Validación básica suficiente para su caso).
    """
    if len(ident) != 13 or not ident.isdigit():
        return False

    # primeros 10 como cédula:
    if not es_cedula_ec_valida(ident[:10]):
        return False

    # últimos 3 no sean "000"
    if ident[10:] == "000":
        return False

    return True


def es_identificacion_valida_cedula_o_ruc(ident: str) -> tuple[bool, str]:
    """
    Devuelve (es_valida, tipo) donde tipo es 'CEDULA', 'RUC' o ''.
    """
    if not ident or not ident.isdigit():
        return False, ""

    if len(ident) == 10:
        return es_cedula_ec_valida(ident), "CEDULA"
    elif len(ident) == 13:
        return es_ruc_persona_natural_valido(ident), "RUC"
    else:
        return False, ""
