from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from django.shortcuts import redirect

def vendedor_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        # Verificar si el usuario está autenticado y pertenece al grupo de vendedores
        if request.user.is_authenticated and request.user.groups.filter(name='Vendedores').exists():
            # El usuario tiene permiso, se permite el acceso a la vista
            return view_func(request, *args, **kwargs)
        else:
            # El usuario no tiene permiso, redirigir a una página de acceso denegado
            return redirect('/')
    return wrapped_view