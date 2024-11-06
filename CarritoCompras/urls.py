"""
URL configuration for CarritoCompras project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inicio.views import pagina_inicio, pagina_ofertas, obtener_carrito, carrito, registro, ingresar, perfil, verificar_correo, cerrar_sesion, ventas_sesion, operacion_sesion
from productos.views import pagina_productos, articulo
from informacion.views import contactanos, servicios, desarrollo_web, mantenimiento
from ventas.views import inicio_ventas, transacciones_ventas, productos_facturar, reciboPago, generarPdf, pago_pendiente, ventas_caja, buscar_deuda, agregarPago, registro_servicios, generar_recibo_servicios,home_ventas, gastos_ventas, comprobar_ventas_caja, finalizar_servicio, servicios_registros, descargar_pdf_servicios, generardescarga_pdf_servicios, politica_servicios, nuevo_abono, generarrecibo_nuevo_abono, cancelar_servicio, devolver_abono
from operacion.views import stock_operacion, inicio_operacion, caja_operacion, caja_apertura_operacion, comprobar_operacion_caja, gastos_operacion, caja_panel, cerrar_caja
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path('', pagina_inicio),
    path('ofertas/', pagina_ofertas),
    path('productos/<int:id>/', pagina_productos),
    path('obtener_carrito/', obtener_carrito, name='obtener_carrito'),
    path('carrito/', carrito),
    path('perfil/', perfil),
    path('contactanos/', contactanos),
    path('servicios/', servicios),
    path('servicios/desarrollo-web', desarrollo_web),
    path('servicios/mantenimiento', mantenimiento),
    path('registro/', registro, name='registro'),
    path('ingresar/', ingresar, name='ingresar'),
    path('verificar/<str:token>/', verificar_correo),
    path('cerrar-sesion/',cerrar_sesion),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('articulo/', articulo),
    #ventas
    path('ventaspccomputers/', ventas_sesion),
    path('ventas/', home_ventas),
    path('ventas/facturacion', inicio_ventas),
    path('ventas/transacciones', transacciones_ventas),
    path('ventas/pagospendientes', pago_pendiente),
    path('ventas/producto', productos_facturar),
    path('ventas/recibo', reciboPago),
    path('ventas/pdf', generarPdf, name='generarPdf'),
    path('buscar_deuda/', buscar_deuda, name='buscar_cliente'),
    path('ventas/agregarpago/', agregarPago, name='agregarpago'),
    path('ventas/registro_servicios', registro_servicios),
    path('ventas/servicio/politica', politica_servicios),
    path('ventas/servicio/recibo', generar_recibo_servicios),
    path('ventas/servicio/finalizar-servicio', finalizar_servicio),
    path('ventas/servicio/cancelar-servicio', cancelar_servicio),
    path('ventas/registro_servicios/abono/<int:id_servicio>', nuevo_abono),
    path('ventas/registro_servicios/abono/generar_recibo_abono', generarrecibo_nuevo_abono),
    path('ventas/servicio/todos_registros', servicios_registros, name='servicios_registros'),
    path('ventas/servicio/descargar_pdf/<str:encoded_path>/', descargar_pdf_servicios, name='descargar_pdf'),
    path('ventas/devolverabono', devolver_abono),
    #esta url sirve para generar la ventana de descarga desde ajax
    path('ventas/servicio/generardescarga_pdf/<str:encoded_path>/', generardescarga_pdf_servicios, name='generardescarga_pdf'),
    path('ventas/gastos', gastos_ventas),
    path('ventas/ingresos', gastos_ventas),
    path('ventas/caja/comprobar', comprobar_ventas_caja),
    path('ventas/caja', ventas_caja),
    #operacion
    path('operacionpccomputers/', operacion_sesion),
    path('operacion/', inicio_operacion),
    path('operacion/stock', stock_operacion),
    path('operacion/caja', caja_operacion),
    path('operacion/panelcaja', caja_panel),
    path('operacion/gastos', gastos_operacion),
    path('operacion/apertura', caja_apertura_operacion),
    path('operacion/caja/comprobar', comprobar_operacion_caja, name='comprobar_operacion_caja'),
    path('operacion/cerrar_caja', cerrar_caja),
    #path('ventas/recibo', reciboPago,name='h'),
    #path('imprimir', reciboImpreso),
    
    #reseteo contraseñas
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="contraseñaResetear.html"), name='password_reset'),
    path('reset_password_send/',auth_views.PasswordResetDoneView.as_view(template_name="contraseñaEnvio.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name="contraseñaNueva.html"),name='password_reset_confirm'),
    path('reset_password_complete',auth_views.PasswordResetCompleteView.as_view(template_name="contraseñaCompletado.html"),name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
