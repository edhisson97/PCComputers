from django.shortcuts import render, redirect
from .decorators import operador_required
from django.contrib.auth.models import User, Group
from .models import Proveedor, Caja, Gasto, Ingreso
from ventas.models import Registro, Servicio, PagoServicio, PagoServicioCombinado, PagoPendienteCombinado, PagoRegistroCombinado, Pago, Equipo, DescripcionEquipo
from productos.models import Producto, Categoria, subCategoria, Marca, ImagenProducto, ColorStock
from operacion.models import ActualizacionStock, ProductosActualizacion
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
import json
from django.template.loader import render_to_string
import tempfile
import pdfkit
import os
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages  # Para mostrar alertas en la plantilla
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
import cloudinary.uploader
from weasyprint import HTML

# Create your views here.
def cerrar_caja(request):
    return render(request, "cierre_caja_recibo.html")

@operador_required
def stock_operacion(request):
    
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        proveedores = Proveedor.objects.all()
    except Proveedor.DoesNotExist:
        return render(request, 'operacion_stock.html', {})
    
    # Crear una lista para almacenar los datos combinados de usuarios y sus datos adicionales
    proveedores_datos = []

    for proveedor_adicional in proveedores:
        datos_adicionales = {
            'ruc': proveedor_adicional.ruc,
            'nombre': proveedor_adicional.nombre,
            'ciudad': proveedor_adicional.ciudad,
            'direccion': proveedor_adicional.direccion,
            'contacto': proveedor_adicional.contacto,
            'email': proveedor_adicional.email,
            'telefono': proveedor_adicional.telefono,
            # Agrega más campos de ser necesario
        }
        proveedores_datos.append(datos_adicionales)
            
    # Convertir la lista de diccionarios a una cadena JSON
    proveedores_json = json.dumps(proveedores_datos)
    
    try:
       todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "operacion_stock.html",)
    
    return render(request, 'operacion_stock.html', {'proveedores':proveedores_json, 'todosProductos':todosProductos})


@operador_required
def inicio_operacion(request):
    
    return render(request, 'operacion_inicio.html', {})

@operador_required
def gastos_operacion(request):
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        caja = Caja.objects.latest('fecha_hora_inicio')
        
        try:
            gastos = Gasto.objects.filter(caja = caja)
        except Gasto.DoesNotExist:
            return render(request, 'operacion_gastos.html', {'caja':caja})
        
        if request.method == 'POST':
            valor = request.POST.get('valor')
            descripcion = request.POST.get('descripcion')
            
            # Crea el objeto Gasto
            nuevo_gasto = Gasto(
                valor=valor,
                descripcion=descripcion,
                caja = caja,
                usuario = request.user
            )
            nuevo_gasto.save()
            gastos = Gasto.objects.filter(caja = caja)
            return render(request, 'operacion_gastos.html', {'caja':caja,'gastos':gastos})
        return render(request, 'operacion_gastos.html', {'caja':caja,'gastos':gastos})
    except Caja.DoesNotExist:
        return render(request, 'operacion_gastos.html', {})
    
@operador_required
def caja_panel(request):
    try:
        caja1 = Caja.objects.filter(numero_caja='Caja_1').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja1 = ''
        
    try:
        caja2 = Caja.objects.filter(numero_caja='Caja_2').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja2 = ''
        
    try:
        caja3 = Caja.objects.filter(numero_caja='Caja_3').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja3 = ''
        
    try:
        caja4 = Caja.objects.filter(numero_caja='Caja_4').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja4 = ''
        
    try:
        caja5 = Caja.objects.filter(numero_caja='Caja_5').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja5 = ''
        
    try:
        caja6 = Caja.objects.filter(numero_caja='Caja_6').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja6 = ''
        
    try:
        caja7 = Caja.objects.filter(numero_caja='Caja_7').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja7 = ''
        
    try:
        caja8 = Caja.objects.filter(numero_caja='Caja_8').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja8 = ''
        
    try:
        caja9 = Caja.objects.filter(numero_caja='Caja_9').latest('fecha_hora_inicio')
    except Caja.DoesNotExist:
        caja9 = ''
    
    return render(request, 'operacion_caja_panel.html',{'caja1':caja1,'caja2':caja2,'caja3':caja3,'caja4':caja4,'caja5':caja5,'caja6':caja6,'caja7':caja7,'caja8':caja8,'caja9':caja9})

@operador_required
def caja_operacion(request):
    
    numero_caja = request.GET.get('numero', None)
    
    
    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now()
    # Formatear la fecha y hora si es necesario
    fecha_hora = fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    
    # Obtener el grupo de Tecnicos
    vendedores_group = Group.objects.get(name='Vendedores')

    # Obtener todos los usuarios que pertenecen al grupo de vendedores
    vendedores = User.objects.filter(groups__in=[vendedores_group])
        
    # Obtén los cajeros de las cajas abiertas
    cajeros_con_caja_abierta = Caja.objects.filter(estado='abierta').values_list('cajero', flat=True)

    # Filtra los vendedores para excluir aquellos que tienen una caja abierta
    vendedores = vendedores.exclude(id__in=cajeros_con_caja_abierta)
    
    try:
        # Usando select_related para obtener los datos adicionales de cada usuario
        caja = Caja.objects.filter(numero_caja=numero_caja).latest('fecha_hora_inicio')
        
    except Caja.DoesNotExist:
        return render(request, 'operacion_caja.html', {'fecha':fecha_hora,'vendedores':vendedores,'numero_caja':numero_caja})
    
    return render(request, 'operacion_caja.html', {'fecha':fecha_hora, 'caja':caja,'vendedores':vendedores,'numero_caja':numero_caja})

@operador_required
def caja_apertura_operacion(request):
    if request.method == 'POST':
        valor_apertura_caja = request.POST.get('apertura_caja')  # Aquí está el cambio
        numero_caja = request.POST.get('numero-caja-hidden')
        vendedor = request.POST.get('vendedor')
        
        user = User.objects.get(username=vendedor)
        
        if valor_apertura_caja:
            valor_apertura_caja = Decimal(valor_apertura_caja)
        else:
            valor_apertura_caja = Decimal(0.00)
        observaciones = request.POST.get('observaciones')
        cajaNueva = Caja()
        cajaNueva.numero_caja = numero_caja
        cajaNueva.cajero = user
        cajaNueva.valor_apertura = valor_apertura_caja
        cajaNueva.observaciones = observaciones
        
        try:
            cajaNueva.save()
            #caja = Caja.objects.latest('fecha_hora_inicio')
            # Enviar el mensaje de éxito junto con la respuesta renderizada
            #return render(request, 'operacion_caja.html', {'mensaje': 'Caja iniciada con éxito','caja':caja})
            #return redirect('/operacion/caja')
            
            #realizo las consultas necesarias para redirigir a la pagina
            #caja = Caja.objects.filter(numero_caja=numero_caja).latest('fecha_hora_inicio')
            
            #fecha_hora_actual = datetime.now()
            #fecha_hora = fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')
            #return render(request, 'operacion_caja.html', {'fecha':fecha_hora, 'caja':caja,'numero_caja':numero_caja})
            return redirect('/operacion/panelcaja')
        except Exception as e:
            # Enviar el mensaje de error junto con la respuesta renderizada
            return render(request, 'operacion_caja.html', {'error': 'Error al iniciar la caja: ' + str(e)})
        
@operador_required
def comprobar_operacion_caja(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            efectivoContado = data.get('efectivo', None)
            #print(efectivoContado)
            cajero_username = data.get('cajero', None)
            accion = data.get('accion', None)
            #print('--------------------------------')
            #print(cajero_username)
            vendedor = User.objects.get(username=cajero_username)
            #print('-------------------')
            #print(vendedor)
            caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
            #print('----------------------------------------------------')
            #print(caja)
            # Aquí puedes procesar los datos como necesites
            #caja = Caja.objects.latest('fecha_hora_inicio')
            
            # Obtener la fecha y hora de inicio de la caja
            fecha_inicio = caja.fecha_hora_inicio
            
            # Obtener la fecha y hora actual
            fecha_actual = timezone.now()
            
            # Filtrar los registros que están dentro del rango de fecha desde fecha_inicio hasta fecha_actual
            registros = Registro.objects.filter(fecha_hora__range=(fecha_inicio, fecha_actual))
            pagosRegistros = Pago.objects.filter(fecha_hora__range=(fecha_inicio, fecha_actual))

            fondoCaja = Decimal(caja.valor_apertura)
            
            totalVendido = 0
            transferencias_ventas = 0
            cheques_ventas = 0
            tarjetas_ventas = 0
            numero_ventas = registros.count()
            numero_ventas_contado = 0
            numero_ventas_credito = 0
            numero_ventas_apartado = 0
            tarjetas_credito_ventas = 0
            tarjetas_debito_ventas = 0
            
            for r in registros:
                if r.tipo_venta == 'Contado':
                    numero_ventas_contado += 1
                    if r.tipo_pago == 'Efectivo':
                        totalVendido = totalVendido + Decimal(r.total_vendido)
                    if r.tipo_pago == 'Transferencia':
                        transferencias_ventas = transferencias_ventas + Decimal(r.total_vendido)
                    if r.tipo_pago == 'Tarjeta de Crédito':
                        tarjetas_ventas = tarjetas_ventas + Decimal(r.total_vendido)
                        tarjetas_credito_ventas = tarjetas_credito_ventas + Decimal(r.total_vendido)
                    if r.tipo_pago == 'Tarjeta de Débito':
                        tarjetas_ventas = tarjetas_ventas + Decimal(r.total_vendido)
                        tarjetas_debito_ventas = tarjetas_debito_ventas + Decimal(r.total_vendido)
                    if r.tipo_pago == 'Cheque':
                        cheques_ventas = cheques_ventas + Decimal(r.total_vendido)
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
                if r.tipo_venta == 'Crédito':
                    numero_ventas_credito +=1
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
                if r.tipo_venta == 'Apartado':
                    numero_ventas_apartado += 1
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
                #if pr.deuda.registro.tipo_venta != "Apartado":
                if pr.tipoPago == 'Efectivo':
                    totalVendido = totalVendido + Decimal(pr.cuota)
                if pr.tipoPago == 'Transferencia':
                    transferencias_ventas = transferencias_ventas + Decimal(pr.cuota)
                if pr.tipoPago == 'Tarjeta de Crédito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(pr.cuota)
                    tarjetas_credito_ventas = tarjetas_credito_ventas + Decimal(pr.cuota)
                if pr.tipoPago == 'Tarjeta de Débito':
                    tarjetas_ventas = tarjetas_ventas + Decimal(pr.cuota)
                    tarjetas_debito_ventas = tarjetas_debito_ventas + Decimal(pr.cuota)
                if pr.tipoPago == 'Cheque':
                    cheques_ventas = cheques_ventas + Decimal(pr.cuota)
                if pr.tipoPago == 'Combinado':
                    try:
                        pagoPendienteCombinado = PagoPendienteCombinado.objects.get(pago = pr)
                        if pagoPendienteCombinado.valorEfectivo:
                            totalVendido = totalVendido + Decimal(pagoPendienteCombinado.valorEfectivo)
                        if pagoPendienteCombinado.valorTarjetaCredito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoPendienteCombinado.valorTarjetaCredito)
                            tarjetas_credito_ventas = tarjetas_credito_ventas + Decimal(pagoPendienteCombinado.valorTarjetaCredito)
                        if pagoPendienteCombinado.valorTarjetaDebito:
                            tarjetas_ventas = tarjetas_ventas + Decimal(pagoPendienteCombinado.valorTarjetaDebito)
                            tarjetas_debito_ventas = tarjetas_debito_ventas + Decimal(pagoPendienteCombinado.valorTarjetaDebito)
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
            tarjetas_credito_servicios = 0
            tarjetas_debito_servicios = 0
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
                        tarjetas_credito_servicios = tarjetas_credito_servicios + Decimal(s.abono)
                    if s.tipoPago == 'Tarjeta de Débito':
                        tarjetas_servicios = tarjetas_servicios + Decimal(s.abono)
                        tarjetas_debito_servicios = tarjetas_debito_servicios + Decimal(s.abono)
                    if s.tipoPago == 'Combinado':
                        try:
                            pagoCombinado = PagoServicioCombinado.objects.get(pagoServicio = s)
                            if pagoCombinado.valorEfectivo:
                                total_servicios = total_servicios + Decimal(pagoCombinado.valorEfectivo)
                            if pagoCombinado.valorTarjetaCredito:
                                tarjetas_servicios = tarjetas_servicios + Decimal(pagoCombinado.valorTarjetaCredito)
                                tarjetas_credito_servicios = tarjetas_credito_servicios + Decimal(pagoCombinado.valorTarjetaCredito)
                            if pagoCombinado.valorTarjetaDebito:
                                tarjetas_servicios = tarjetas_servicios + Decimal(pagoCombinado.valorTarjetaDebito)
                                tarjetas_debito_servicios = tarjetas_debito_servicios + Decimal(pagoCombinado.valorTarjetaDebito)
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
            
            aux = ''
            #compruebo que el total efectivo no sea negativo
            if totalEfectivo > 0:
                diferencia = Decimal(totalEfectivo) - Decimal(efectivoContado)
                # Determinar el sobrante o el faltante basado en la diferencia
                if diferencia < 0:
                    sobrante = abs(diferencia)
                    aux = "sobra"
                elif diferencia > 0:
                    faltante = abs(diferencia)
                    aux = "falta"
            else:
                diferencia = Decimal(totalEfectivo) + Decimal(efectivoContado)
                # Determinar el sobrante o el faltante basado en la diferencia
                if diferencia > 0:
                    sobrante = abs(diferencia)
                    aux = "sobra"
                elif diferencia < 0:
                    faltante = abs(diferencia)
                    aux = "falta"
            
            totalCheques = cheques_ventas + cheques_servicios
            totalTransferencias = transferencias_servicios + transferencias_ventas
            totalTarjetas = tarjetas_servicios + tarjetas_ventas
        
        except Exception as e:
            import traceback
            #print("❌ ERROR FUERA de cerrar:")
            #print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)
        
        # Devuelve una respuesta JSON
        if accion == 'cerrar':
            try:
                detalle = data.get('detalle', None)
                ventas = totalVendido + cheques_ventas + tarjetas_credito_ventas + tarjetas_debito_ventas + transferencias_ventas
                servicios = total_servicios + cheques_servicios + tarjetas_credito_servicios + tarjetas_debito_servicios + transferencias_servicios
                totalGeneral = ventas + servicios
                fechaCierre = timezone.now()
                
                context = {
                'aperturaCaja':caja.fecha_hora_inicio,
                'cierreCaja':fechaCierre,
                'cajero':caja.cajero.first_name +" " +caja.cajero.last_name +" ("+caja.cajero.username+")",
                'numeroCaja':caja.id,
                'detalle':detalle,
                'numero_ventas':numero_ventas,
                'numero_ventas_contado':numero_ventas_contado,
                'numero_ventas_credito':numero_ventas_credito,
                'numero_ventas_apartado':numero_ventas_apartado,
                'enEfectivo':totalVendido,
                'chequesVentas':cheques_ventas,
                'tarjetas_credito_ventas':tarjetas_credito_ventas,
                'tarjetas_debito_ventas':tarjetas_debito_ventas,
                'transferenciasVentas':transferencias_ventas,
                'ventas_contado':ventas,
                'efectivoServicios':total_servicios,
                'chequesServicios':cheques_servicios,
                'tarjetas_credito_servicios':tarjetas_credito_servicios,
                'tarjetas_debito_servicios':tarjetas_debito_servicios,
                'transferencias_servicios':transferencias_servicios,
                'totalServicios': servicios,
                #'ventasContado': totalVendido + cheques_ventas + tarjetas_credito_ventas + tarjetas_debito_ventas + transferencias_ventas,
                'efectivoContado': efectivoContado,
                'inicioCaja':fondoCaja,
                'totalGeneral': totalGeneral,
                'totalEgresos':totalEgresos,
                'totalIngresos':totalIngresos,
                'totalEfectivo':totalEfectivo,
                'aux':aux,
                }
                
                
                ###         PARA WHTMLTOPDF
                #generar pdf y enviar
                #html_content = render_to_string('cierre_caja_recibo.html', context)

                # Guardar el contenido HTML en un archivo temporal
                #with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
                #    temp_html.write(html_content.encode('utf-8'))
                #    temp_html_path = temp_html.name
                    
                    # Cerrar el archivo HTML temporal
                #    temp_html.close()
                    # Eliminar el archivo PDF temporal
            
                #wkhtmltopdf_path = getattr(settings, 'WKHTMLTOPDF_PATH', None)

                #if not wkhtmltopdf_path or not os.path.exists(wkhtmltopdf_path):
                #    return JsonResponse({'error': 'wkhtmltopdf no está disponible en el servidor'}, status=500)


                # Configuración de pdfkit
                #config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
            
                # Convertir el archivo HTML temporal a PDF
                #output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
                #pdfkit.from_file(temp_html_path, output_path, configuration=config)
                
                # Suponiendo que tienes output_path definido y quieres codificarlo
                #encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))

                #### PARA WEASYPRINT
                # Generar PDF y enviar
                html_content = render_to_string('cierre_caja_recibo.html', context)

                # Convertir directamente a PDF usando WeasyPrint
                #with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output_pdf:
                output_path = tempfile.mktemp(suffix='.pdf')
                HTML(string=html_content).write_pdf(output_path)

                # Codificar la ruta
                encoded_path = urlsafe_base64_encode(output_path.encode('utf-8'))
                
                
                
                
                
                # Crear el diccionario de contexto
                context = {'encoded_path': encoded_path}
                
                caja.estado = "cerrada"
                caja.fecha_hora_cierre = fechaCierre
                caja.observaciones = detalle
                caja.efectivo_ventas = totalVendido
                caja.total_ventas = ventas
                caja.efectivo_servicios = total_servicios
                caja.total_servicios = servicios
                caja.total_general = totalGeneral
                caja.efectivo_contado = efectivoContado
                caja.save()
                
                return JsonResponse(context)
            except Exception as e:
                import traceback
                print("EL ERROR ES: ")
                print(traceback.format_exc())  # Verás esto en los logs de Render
                return JsonResponse({'error': str(e)}, status=500)
        else:
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
            return JsonResponse(response_data)

    # Si la solicitud no es POST, devolver un error apropiado (en desarrollo, puede ser 405 Method Not Allowed)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@operador_required
def descargar_pdf_operaciones(request, encoded_path):
    # Decodificar la ruta del archivo
    decoded_path = urlsafe_base64_decode(encoded_path).decode('utf-8')
    
    with open(decoded_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="recibo_cierre_caja.pdf"'
    return response

@operador_required
def generardescarga_pdf_operaciones(request, encoded_path):
    # Decodificar la ruta del archivo
    context = {'encoded_path': encoded_path}
    return render(request, 'descargar_pdf_cierrecaja.html', context)

@operador_required
def nuevo_producto(request):
    try:
        categoria = Categoria.objects.all()
        primeraCategoria = Categoria.objects.first()
    except Categoria.DoesNotExist:
        return render(request, "operacion_stock.html")

    try:
        subcategoria = subCategoria.objects.all()
    except subCategoria.DoesNotExist:
        return render(request, "operacion_stock.html")

    try:
        marca = Marca.objects.all()
    except Marca.DoesNotExist:
        return render(request, "operacion_stock.html")

    try:
        primerasSubcategorias = subCategoria.objects.filter(id_categoria=primeraCategoria.id)
    except subCategoria.DoesNotExist:
        primerasSubcategorias = "Ninguna"

    subcategorias_dict = [
        {"id": sub.id, "nombre": sub.nombre, "id_categoria": sub.id_categoria.nombre}
        for sub in subcategoria
    ]

    subcategorias_json = json.dumps(subcategorias_dict)

    if request.method == "POST":
        try:
            modelo = request.POST.get("modelo")
            calidad = request.POST.get("calidad")
            detalle = request.POST.get("detalle")
            descripcion = request.POST.get("descripcion")
            oferta = request.POST.get("oferta") == "on"
            precio_oferta = request.POST.get("precio_oferta") if oferta else None
            imagenes = request.FILES.getlist("imagenes")
            precio = request.POST.get("precio")
            peso = request.POST.get("peso")
            categoria_id = request.POST.get("categoria")
            subcategoria_id = request.POST.get("subcategoria")
            marca_id = request.POST.get("marca")

            nuevo_producto = Producto(
                modelo=modelo,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                marca_id=marca_id,
                calidad=calidad,
                precio=precio,
                detalle=detalle,
                descripcion=descripcion,
                peso=peso,
                oferta=oferta,
                precio_oferta=precio_oferta,
                desactivado = 'si'
            )
            nuevo_producto.save()

            for imagen in imagenes:
                ImagenProducto.objects.create(producto=nuevo_producto, imagen=imagen)

            colorStock = ColorStock(
                color='',
                stock=0,
                producto=nuevo_producto,
            )
            colorStock.save()

            return redirect(f"/operacion/stock/nuevoproducto/detalle/idproducto={nuevo_producto.id}/")

        except ValueError as ve:
            messages.error(request, f"Error de valor: {str(ve)}")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {str(e)}")

        # SOLUCIÓN: Siempre retornar `render()` si hay un error
        return render(request, 'operacion_crearproducto.html', {
            "categorias": categoria,
            "subcategorias": subcategorias_json,
            "marcas": marca,
            "primerasSubcategorias": primerasSubcategorias
        })

    # Respuesta en caso de `GET`
    return render(request, 'operacion_crearproducto.html', {
        "categorias": categoria,
        "subcategorias": subcategorias_json,
        "marcas": marca,
        "primerasSubcategorias": primerasSubcategorias
    })
    
@operador_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    tiene_color_valido = ColorStock.objects.filter(
            producto=producto,
            color__isnull=False,
            color__gt="",
            stock__gt=0
            ).exists()
    if request.method == "POST":
        try:
            # Capturar los datos del formulario
            codigo_referencial = request.POST.get("codigoReferencial")
            nombre_color = request.POST.get("color")
            codigo_color = request.POST.get("codigo_color")  # Hexadecimal
            stock = request.POST.get("stock")
            imagen = request.FILES.get("imagen")
            
            nuevoColorStock = ColorStock()
            nuevoColorStock.codigo_referencial = codigo_referencial
            nuevoColorStock.color = nombre_color
            nuevoColorStock.codigo_color = codigo_color
            nuevoColorStock.stock = int(stock)
            if imagen:
                nuevoColorStock.imagen =imagen
            nuevoColorStock.producto = producto
            nuevoColorStock.save()
            
            if not tiene_color_valido:
                producto.desactivado = ''
                producto.save()
            
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe.")
        except Exception as e:
            messages.error(request, f"Error al agregar el color: {str(e)}")
            
    existe_stock = ColorStock.objects.filter(stock__gt=0).exists()
    
    colores = ColorStock.objects.filter(producto=producto)

    return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores,"existe_stock":existe_stock})

@operador_required
def todos_productos(request):
    productos = Producto.objects.all()
    return render(request, "operacion_todosproductos.html", {"productos": productos})

@operador_required
def editar_color(request):
    if request.method == "POST":
        color_id = request.POST.get("id")
        color_obj = get_object_or_404(ColorStock, id=color_id)
        
        # Si el usuario marcó la opción de eliminar la imagen
        if request.POST.get("eliminar_imagen"):
            if color_obj.imagen:  # Verifica que haya una imagen
                public_id = color_obj.imagen.public_id  # Obtiene el ID de la imagen en Cloudinary
                cloudinary.uploader.destroy(public_id)  # Elimina la imagen de Cloudinary
                color_obj.imagen = None  # Limpia el campo en la base de datos

        # Si el usuario subió una nueva imagen
        elif 'imagen' in request.FILES:
            color_obj.imagen = request.FILES['imagen']  # Actualiza con la nueva imagen
        
        color_obj.color = request.POST.get("color")
        color_obj.codigo_referencial = request.POST.get("codigo_referencial")
        color_obj.stock = request.POST.get("stock")
        color_obj.codigo_color = request.POST.get("codigo_color")

        color_obj.save()
        messages.success(request, "Color actualizado correctamente.")
        
        producto = get_object_or_404(Producto, id=color_obj.producto.id)
        colores = ColorStock.objects.filter(producto=producto)
        return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores})
    
@operador_required
def eliminar_color(request, color_id):
    color = get_object_or_404(ColorStock, id=color_id)

    if request.method == "POST":
        if color.imagen:  # Verifica que haya una imagen
                public_id = color.imagen.public_id  # Obtiene el ID de la imagen en Cloudinary
                cloudinary.uploader.destroy(public_id)  # Elimina la imagen de Cloudinary
        
        color.delete()
        messages.success(request, "Color eliminado correctamente.")
        
    producto = get_object_or_404(Producto, id=color.producto.id)
    colores = ColorStock.objects.filter(producto=producto)
    return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores})
    

    
@operador_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        categoria = []

    try:
        subcategoria = subCategoria.objects.all()
    except subCategoria.DoesNotExist:
        subcategoria = []

    try:
        marca = Marca.objects.all()
    except Marca.DoesNotExist:
        marca = []
    
    # Esto se hace para cargar el producto en el formulario
    categorias_seleccionada = producto.categoria.id if producto.categoria else None
    subcategorias_seleccionada = producto.subcategoria.id if producto.subcategoria else None
    marca_seleccionada = producto.marca.id if producto.marca else None
    
    precio = "{:.2f}".format(producto.precio)  # Asegura que el precio tiene dos decimales
    peso = "{:.2f}".format(producto.peso)
    if producto.precio_oferta:
        oferta = "{:.2f}".format(producto.precio_oferta)
    
        return render(request, "operacion_editarproducto.html", {
            "producto": producto,
            "categoria": categoria,
            "subcategoria": subcategoria,
            "marca": marca,
            "categorias_seleccionada": categorias_seleccionada,
            "subcategorias_seleccionada": subcategorias_seleccionada,
            "marca_seleccionada": marca_seleccionada,
            "precio":precio,
            "peso":peso,
            "precio_oferta":oferta
        })
    else:
        return render(request, "operacion_editarproducto.html", {
        "producto": producto,
        "categoria": categoria,
        "subcategoria": subcategoria,
        "marca": marca,
        "categorias_seleccionada": categorias_seleccionada,
        "subcategorias_seleccionada": subcategorias_seleccionada,
        "marca_seleccionada": marca_seleccionada,
        "precio":precio,
        "peso":peso,
    })
    
@operador_required
def actualizar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        # Obtener datos del formulario
        producto.modelo = request.POST.get("modelo")
        subcategoria_id = request.POST.get("subcategoria")
        subcategoria = get_object_or_404(subCategoria, id=subcategoria_id)
        categoria = get_object_or_404(Categoria, nombre=subcategoria.id_categoria)
        producto.subcategoria = subcategoria
        producto.categoria = categoria
        marca_id = request.POST.get("marca")
        marca = get_object_or_404(Marca, id=marca_id)
        producto.marca = marca
        producto.calidad = request.POST.get("calidad")

        # Manejo de números (precio y peso)
        try:
            producto.precio = float(request.POST.get("precio", 0))
            producto.peso = float(request.POST.get("peso", 0))
        except ValueError:
            messages.error(request, "Error en los valores numéricos.")
            return redirect("actualizar_producto", producto_id=producto.id)

        producto.detalle = request.POST.get("detalle")
        producto.descripcion = request.POST.get("descripcion")

        # Manejo del checkbox de oferta
        if "oferta" in request.POST:
            producto.oferta = True
            try:
                producto.precio_oferta = float(request.POST.get("precio_oferta", 0))
            except ValueError:
                producto.precio_oferta = None
        else:
            producto.oferta = False
            producto.precio_oferta = None

        # Guardar cambios
        producto.save()
        messages.success(request, "Producto actualizado correctamente.")

        # Redirigir a la vista de detalles del producto (ajusta según tu proyecto)
        producto = get_object_or_404(Producto, id=producto_id)
        colores = ColorStock.objects.filter(producto=producto)
        return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores})

@operador_required
def gestionar_imagenes(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    imagenes = ImagenProducto.objects.filter(producto=producto)

    if request.method == "POST":
        if "agregar" in request.POST and "imagen" in request.FILES:
            if imagenes.count() >= 4:
                messages.error(request, "No puedes subir más de 4 imágenes.")
            else:
                nueva_imagen = ImagenProducto(producto=producto, imagen=request.FILES["imagen"])
                nueva_imagen.save()
                messages.success(request, "Imagen agregada con éxito.")
                return redirect("gestionar_imagenes", producto_id=producto.id)
        
        elif "eliminar" in request.POST:
            imagen_id = request.POST.get("imagen_id")
            imagen = get_object_or_404(ImagenProducto, id=imagen_id, producto=producto)
            public_id = imagen.imagen.public_id  # Obtiene el ID de la imagen en Cloudinary
            cloudinary.uploader.destroy(public_id)
            imagen.delete()
            messages.success(request, "Imagen eliminada correctamente.")
            return redirect("gestionar_imagenes", producto_id=producto.id)

    return render(request, "operacion_gestionarimagenes.html", {"producto": producto, "imagenes": imagenes})

@operador_required
def desactivar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == "GET":
        producto.desactivado = "si"
        producto.save()
        messages.success(request, f"El producto '{producto.modelo}' ha sido desactivado correctamente.")
    
    # Redirigir a la vista de detalles del producto (ajusta según tu proyecto)
    colores = ColorStock.objects.filter(producto=producto)
    redirect(f'/operacion/stock/nuevoproducto/detalle/idproducto={producto.id}/')
    return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores})

@operador_required
def activar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "GET":    
        # Buscar si existe al menos un color válido
        
        tiene_color_valido = ColorStock.objects.filter(
            producto=producto,
            color__isnull=False,
            color__gt="",
            stock__gt=0
            ).exists()
        
        if tiene_color_valido:
            producto.desactivado = ""
            producto.save()
            messages.success(request, f"El producto '{producto.modelo}' ha sido activado correctamente.")
        else:
            messages.success(request, f"El producto '{producto.modelo}' no puede ser activao porque no tiene colores disponible, por favor agregue un color para activar el producto.")
    colores = ColorStock.objects.filter(producto=producto)
    return redirect(f'/operacion/stock/nuevoproducto/detalle/idproducto={producto.id}/')
    return render(request, "operacion_detalleproducto.html", {"producto": producto,"colores": colores})


@operador_required
def productos_actualizarStock(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Obtén los datos del cuerpo de la solicitud
        productos_stock = data.get('productosStock', None)  # Obtiene los productos
        
        productos_actualizar_stock = []
        
        if productos_stock:
            # Procesa los productos como desees
            for producto in productos_stock:
                id_producto = producto.get('id')
                color = producto.get('color')
                cantidad = producto.get('cantidad')
          
                try:
                    #producto_bd = Producto.objects.get(id=id_producto)
                    producto_bd = get_object_or_404(Producto.objects.exclude(desactivado="si"), id=id_producto)
                    # Realiza las operaciones necesarias con el producto obtenido
                except Producto.DoesNotExist:
                    return JsonResponse({'error': 'Datos no encontrados'}, )
                #reviso si producto tiene oferta
                if (producto_bd.precio_oferta):
                    precio = producto_bd.precio_oferta
                else:
                    precio = producto_bd.precio
               
                productos_actualizar_stock.append({
                    'id': producto_bd.id,
                    'modelo': producto_bd.modelo,
                    #'marca': marca_info,
                    'color':color,
                    'cantidad':cantidad,
                    'precio': precio,
                    'precio_oferta': producto_bd.precio_oferta,
                    'detalle': producto_bd.detalle
                    # Agrega otros campos que necesites
                })
               
            
            # Devuelve una respuesta exitosa
            return JsonResponse({'productos': productos_actualizar_stock})
        else:
            # Si no se proporcionaron datos adecuados, devuelve un error
            return JsonResponse({'error': 'Datos no proporcionados correctamente 1'}, status=400)
    else:
        # Si la solicitud no es de tipo POST, devuelve un error
        return JsonResponse({'error': 'Método no permitido 2'}, status=405)

@operador_required
def guardar_stock(request):
    if request.method == "POST":
        try:
            # Obtener los datos enviados en formato JSON
            data = json.loads(request.body)

            # Extraer los datos del proveedor
            proveedor_data = data.get("proveedor", {})
            descripcion = data.get("descripcion", "")
            numeroFactura = data.get("numeroFactura","")
            productos = data.get("productos", [])

            print(numeroFactura)
            # Validar que hay productos
            if not productos:
                return JsonResponse({"success": False, "error": "No hay productos para guardar"}, status=400)

             # Buscar o actualizar el proveedor
            proveedor, created = Proveedor.objects.update_or_create(
                ruc=proveedor_data.get("ruc"),
                defaults={
                    "nombre": proveedor_data.get("nombre"),
                    "ciudad": proveedor_data.get("ciudad"),
                    "direccion": proveedor_data.get("direccion"),
                    "contacto": proveedor_data.get("contacto"),
                    "email": proveedor_data.get("email"),
                    "telfono": proveedor_data.get("celular")
                },
            )
            
             # Crear el registro de actualización de stock
            actualizacion = ActualizacionStock.objects.create(
                proveedor=proveedor,
                descripcion=descripcion,
                numeroFactura=numeroFactura
            )
            
            # Ahora recorremos el array de productos y procesamos cada uno
            for producto in productos:
                
                producto_id = producto.get("id")
                color = producto.get("color")
                cantidad = producto.get("cantidad")
                print(producto_id)
                print(color)
                print(cantidad)
                try:
                    prod = Producto.objects.get(id = producto_id)
                    colorstock = ColorStock.objects.get(producto = prod, color = color)
                    actualcantidad = colorstock.stock
                    colorstock.stock = int(actualcantidad) + int(cantidad)
                    colorstock.save()
                    
                    productoActualizado = ProductosActualizacion.objects.create(
                    actualizacionstock = actualizacion,
                    producto = prod,
                    colorstock = colorstock,
                    cantidad = cantidad)
                    
                except Producto.DoesNotExist:
                    return JsonResponse({"success": False, "message": f"Producto con ID {producto_id} no encontrado."})
                except ColorStock.DoesNotExist:
                    return JsonResponse({"success": False, "message": f"No se encontró el color {color} para el producto {producto_id}."})

            return JsonResponse({"success": True, "message": "Stock guardado con éxito", "id": actualizacion.id})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error en el formato JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

@operador_required
def actualizar_precios(request, id):
    actualizacionStock = get_object_or_404(ActualizacionStock, id=id)
    productosActualizados = ProductosActualizacion.objects.filter(actualizacionstock = actualizacionStock)
    
    # Obtener solo los productos únicos de ProductosActualizacion
    productos_unicos = Producto.objects.filter(
        id__in=ProductosActualizacion.objects.filter(actualizacionstock=actualizacionStock).exclude(precio_actualizado__iexact="si")
        .values_list('producto', flat=True).distinct()
    )
    
    return render(request, "operacion_actualizarprecios.html", {"productosA": productosActualizados,"productosU":productos_unicos})

@operador_required
def guardar_nuevoprecio(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto_id = data.get("producto_id")
            nuevo_precio = data.get("nuevo_precio")

            if not producto_id or nuevo_precio is None:
                return JsonResponse({"success": False, "message": "Datos inválidos."})

            # Buscar el producto y actualizar el precio
            producto = Producto.objects.get(id=producto_id)
            if (producto.precio_oferta):
                producto.precio_oferta = Decimal(nuevo_precio)
            else:
                producto.precio = Decimal(nuevo_precio)
            producto.save()
            
            productosActualizacion = ProductosActualizacion.objects.filter(producto=producto)
            for prodAct in productosActualizacion:
                prodAct.precio_actualizado = 'si'
                prodAct.save()
            
            messages.success(request, "Precio actualizado con éxito.")
            

            return JsonResponse({"success": True, "message": "Precio actualizado correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@operador_required
def ofertas(request):
    # Obtener el valor del parámetro 'option' de la URL
    option = request.GET.get('option', 'default_value')  # 'default_value' es un valor por defecto
    
    try:
        if option == 'Ofertas':
            productos = Producto.objects.filter(oferta=True)
        elif option == 'sinOfertas':
            productos = Producto.objects.filter(oferta=False)
        else:
           productos = Producto.objects.all()
            
        colorStock = ColorStock.objects.all()
    
    except Exception as e:
        # Capturar errores y enviar mensaje de error
        mensaje_error = f"Ocurrió un error al obtener los datos: {str(e)}"
        return render(request, "operacion_ofertas.html", {"mensaje_error": mensaje_error})

    return render(request, "operacion_ofertas.html", {"productos": productos,"colorStock":colorStock})

@operador_required
def agregar_oferta(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto_id = data.get("producto_id")
            nuevo_precio = data.get("nuevo_precio")
            
            if not producto_id or nuevo_precio is None:
                return JsonResponse({"success": False, "message": "Datos inválidos."})
            
            # Buscar el producto y actualizar el precio
            producto = Producto.objects.get(id=producto_id)
            
            if producto.precio < Decimal(nuevo_precio):
                return JsonResponse({"success": False, "message": "El precio de oferta no puede ser mayor al precio de venta."})

            
            producto.precio_oferta = Decimal(nuevo_precio)
            producto.oferta = True
            producto.save()
            
            
            messages.success(request, "Oferta actualizada con éxito.")
            

            return JsonResponse({"success": True, "message": "Oferta actualizada con éxito."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@operador_required
def quitar_oferta(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto_id = data.get("producto_id")
            
            # Buscar el producto y actualizar el precio
            producto = Producto.objects.get(id=producto_id)

            
            producto.precio_oferta = None
            producto.oferta = False
            producto.save()
            
            
            messages.success(request, "Oferta quitada correctamente.")
            

            return JsonResponse({"success": True, "message": "Oferta quitada correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    return JsonResponse({"success": False, "message": "Método no permitido."})

@operador_required
def todos_equipos(request):
    nuevo_nombre = request.GET.get("nuevo")
    if nuevo_nombre:
        equipo = Equipo.objects.create(
            nombre = nuevo_nombre
        )
        return redirect("/operacion/todosequipos")
    equipos = Equipo.objects.all()
    return render(request, "operacion_todosequipos.html", {"equipos": equipos})

@operador_required
def detalles_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        
        if tipo == "eliminarEquipo":
            equipo_id = request.POST.get("equipo_id")
            equipod = Equipo.objects.get(id = equipo_id)
            equipod.delete()
            equipos = Equipo.objects.all()
            messages.success(request, "✅ El equipo ha sido eliminado correctamente.")
            return render(request, "operacion_todosequipos.html", {"equipos": equipos})
        
        elif tipo == "crearProblema":
            problema = request.POST.get("problema")
            costo = request.POST.get("costo")
            nuevoProblema = DescripcionEquipo()
            nuevoProblema.equipo = equipo
            nuevoProblema.problema = problema
            nuevoProblema.costo = int(costo)      
            nuevoProblema.save()    
            messages.success(request, "✅ El problema a sido creado correctamente.")
        
        elif tipo == "editarProblema":
            id = request.POST.get("edit-id")
            problema = request.POST.get("edit-problema")
            costo = request.POST.get("edit-costo")
            desProblema = DescripcionEquipo.objects.get(id=id)
            desProblema.problema = problema
            desProblema.costo = int(costo)      
            desProblema.save()    
            messages.success(request, "✅ El problema a sido editado correctamente.")
            
        elif tipo == "eliminarProblema":
            id = request.POST.get("delete_problema_id")
            costo = request.POST.get("edit-costo")
            desProblema = DescripcionEquipo.objects.get(id=id)
            desProblema.delete()
            messages.success(request, "✅ El problema a sido eliminado correctamente.")
            
        elif tipo == "editarEquipo":
            equipo_id = request.POST.get("edit-equipo-id")
            print(equipo_id)
            nombre = request.POST.get("nombre-equipo")
            equipo = Equipo.objects.get(id = equipo_id)
            equipo.nombre = nombre
            equipo.save()
            messages.success(request, "✅ El equipo ha sido editado correctamente.")
            
    problemas = DescripcionEquipo.objects.filter(equipo=equipo)
    return render(request, "operacion_detalleproblemas.html", {"equipo": equipo, "problemas":problemas})

@operador_required
def operador_proveedores(request):
    if request.method == 'POST':
        id = request.POST.get('id', '').strip()
        
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        ruc = request.POST.get('ruc', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        contacto = request.POST.get('contacto', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validaciones básicas
        errores = []
        if not nombre:
            errores.append("El campo 'Nombres' es obligatorio.")
        if not id:
            if len(ruc) != 13 or not ruc.isdigit():
                errores.append("El ruc debe tener 13 dígitos.")
            # Validación de unicidad
            if Proveedor.objects.filter(ruc=ruc).exists():
                errores.append("Ya existe un proveedor con ese ruc.")
            if Proveedor.objects.filter(email=correo).exists():
                errores.append("Ya existe un cliente con ese correo.")
        if not ciudad:
            errores.append("El campo 'Ciudad' es obligatorio.")
        if not direccion:
            errores.append("El campo 'Dirección' es obligatorio.")

        # Si hay errores, mostrar mensajes
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('vistaproveedores')  # Asegúrate que este sea tu URL name
        
        
        if id:
            proveedor = Proveedor.objects.get(id = id)
        else:
            proveedor = Proveedor()
            proveedor.ruc = ruc
        
        proveedor.nombre = nombre
        proveedor.telefono = telefono
        proveedor.email = correo
        proveedor.ciudad = ciudad
        proveedor.direccion = direccion
        proveedor.contacto = contacto
        proveedor.save()
        
        if id:
            messages.success(request, "Proveedor '"+nombre+" - "+ruc+"' editado exitosamente.")
        else:
            messages.success(request, "Proveedor '"+nombre+" - "+ruc+"' creado exitosamente.")
    # Usuarios que NO tienen grupos ni permisos
    proveedores = Proveedor.objects.all()
    
    return render(request, 'operacion_proveedores.html',{"proveedores":proveedores})

@operador_required
def descargar_reportes(request):
    if request.method == "POST":
        tipo_reporte = request.POST.get('tipo_reporte')
        contraseña = request.POST.get('contraseña')
        
        if request.user.check_password(contraseña):
            # ✅ Contraseña correcta: continuar con la lógica
            # Aquí puedes generar el reporte según el tipo
            # return generar_excel(tipo_reporte)
            print('reporte impreso')

        else:
            # ❌ Contraseña incorrecta
            messages.error(request, "Contraseña incorrecta. Intenta de nuevo.")

    return render(request, 'operacion_descargarreportes.html',)