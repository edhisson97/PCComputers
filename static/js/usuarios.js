$('.ventana-emergente').on('click', function (event) {
    if (event.target === this) {
        cerrarVentana();
    }
});

function mostrarVentana() {
    $('#ventanaEmergente').show();
}

function cerrarVentana() {
    $('#ventanaEmergente').hide();
    document.getElementById('formularioInicioSesion').style.display = 'block';
    document.getElementById('linkRecuperarContrasena').style.display = 'block';
    //document.getElementById('recuperarContrasena').style.display = 'none';
    document.getElementById('registrar').style.display = 'none';
    document.getElementById('btn-registrar').style.display = 'block';
}


/******************validar campos */
document.getElementById('correo').addEventListener('blur', validarCampo);
document.getElementById('contrasena').addEventListener('blur', validarCampo);

function validarCampo(event) {
    const campo = event.target;
    const mensajeErrorId = 'mensaje' + campo.id.charAt(0).toUpperCase() + campo.id.slice(1);

    if (campo.value.trim() === '') {
        document.getElementById(mensajeErrorId).innerText = 'Por favor, complete este campo.';
    } else {
        document.getElementById(mensajeErrorId).innerText = '';
    }
}


/************************cambiar datos a recuperar contraseña */
/*function mostrarRecuperarContrasena() {
    // Ocultar campos de inicio de sesión
    document.getElementById('formularioInicioSesion').style.display = 'none';
    document.getElementById('linkRecuperarContrasena').style.display = 'none';
    // Mostrar formulario de recuperación de contraseña
    document.getElementById('recuperarContrasena').style.display = 'block';
}*/

function mostrarRegistro() {
    // Ocultar campos de inicio de sesión
    document.getElementById('formularioInicioSesion').style.display = 'none';
    document.getElementById('linkRecuperarContrasena').style.display = 'none';
    document.getElementById('registrar').style.display = 'block';
    document.getElementById('btn-registrar').style.display = 'none';
    //document.getElementById('recuperarContrasena').style.display = 'none';
    // Mostrar formulario de recuperación de contraseña
    
}

function iniciarSesion() {
    document.getElementById('formularioInicioSesion').style.display = 'block';
    document.getElementById('linkRecuperarContrasena').style.display = 'block';
    //document.getElementById('recuperarContrasena').style.display = 'none';
    document.getElementById('registrar').style.display = 'none';
    document.getElementById('btn-registrar').style.display = 'block';
}

/*function cerrarVentana() {
    // Restaurar visibilidad de campos de inicio de sesión y ocultar formulario de recuperación
    document.getElementById('formularioInicioSesion').style.display = 'block';
    document.getElementById('recuperarContrasena').style.display = 'none';

    // Cerrar la ventana emergente (agrega tu lógica de cierre aquí)
}*/
