from django.shortcuts import render
from inicio.models import Categoria
from productos.models import Producto
from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings

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

def quienes_somos(request):
    try:
        categoria = Categoria.objects.all()
    except Categoria.DoesNotExist:
        return render(request, "quienes_somos.html",)
    try:
        todosProductos = Producto.objects.exclude(desactivado="si")
    except Producto.DoesNotExist:
        return render(request, "quienes_somos.html",)
    return render(request, 'quienes_somos.html', {"categoria": categoria,"todosProductos":todosProductos})

def contactoWeb(request):
    if request.method == "POST":
        asunto = request.POST.get("asunto")
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        mensaje = request.POST.get("mensaje")

        if not all([asunto, nombre, correo, mensaje]):
            messages.error(request, "❌ Todos los campos son obligatorios.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            mensaje_final = f"""
            Nombre: {nombre}
            Correo: {correo}

            Mensaje:
            {mensaje}
            """

            email = EmailMessage(
                subject=f"Contacto Web - PC Computers: {asunto}",
                body=mensaje_final,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['edhisson97sanmartin@gmail.com'],
                reply_to=[correo],
            )

            email.send(fail_silently=False)


            messages.success(
                request,
                "✅ Tu mensaje fue enviado correctamente. Nos pondremos en contacto contigo pronto."
            )

        except Exception as e:
            print("ERROR EMAIL:", e)
            messages.error(
                request,
                "❌ Ocurrió un error al enviar el mensaje. Inténtalo nuevamente. O envíanos un correo a edhisson97sanmartin@gmail.com"
            )

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect("/codebyedhisson")
