from django.shortcuts import render, redirect
from .decorators import operador_required
from django.contrib.auth.models import User, Group
from .models import Proveedor, Caja, Gasto, Ingreso
from ventas.models import Registro, Servicio, PagoServicio, PagoServicioCombinado, PagoPendienteCombinado, PagoRegistroCombinado, Pago
from productos.models import Producto
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
import json

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
            'numeroFactura': proveedor_adicional.numeroFactura,
            # Agrega más campos de ser necesario
        }
        proveedores_datos.append(datos_adicionales)
            
    # Convertir la lista de diccionarios a una cadena JSON
    proveedores_json = json.dumps(proveedores_datos)
    
    try:
       todosProductos = Producto.objects.all()
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
        data = json.loads(request.body)
        efectivoContado = data.get('efectivo', None)
        print(efectivoContado)
        cajero_username = data.get('cajero', None)
        print('--------------------------------')
        print(cajero_username)
        vendedor = User.objects.get(username=cajero_username)
        print('-------------------')
        print(vendedor)
        caja = Caja.objects.filter(cajero=vendedor).latest('fecha_hora_inicio')
        print('----------------------------------------------------')
        print(caja)
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