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
from inicio.views import pagina_inicio, pagina_ofertas, obtener_carrito, carrito, registro, ingresar, perfil, verificar_correo, cerrar_sesion, ventas_sesion
from productos.views import pagina_productos, articulo
from informacion.views import contactanos, servicios, desarrollo_web, mantenimiento
from ventas.views import inicio_ventas, transacciones_ventas, productos_facturar, reciboPago, generarPdf
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
    path('ventas/', inicio_ventas),
    path('ventas/transacciones', transacciones_ventas),
    path('ventas/producto', productos_facturar),
    path('ventas/recibo', reciboPago),
    path('ventas/pdf', generarPdf, name='generarPdf'),
    #path('ventas/recibo', reciboPago,name='h'),
    #path('imprimir', reciboImpreso),
    
    #reseteo contraseñas
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="contraseñaResetear.html"), name='password_reset'),
    path('reset_password_send/',auth_views.PasswordResetDoneView.as_view(template_name="contraseñaEnvio.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name="contraseñaNueva.html"),name='password_reset_confirm'),
    path('reset_password_complete',auth_views.PasswordResetCompleteView.as_view(template_name="contraseñaCompletado.html"),name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
