window.onload = function() {
    // Llama a tu función aquí
    actualizarTabla();
};




function buscarProveedor() {
    var cedula = document.getElementById("ruc").value;
    var proveedoresString = document.getElementById("ruc").getAttribute("data-proveedores");
    var usuarios = JSON.parse(proveedoresString);
    
    // Variable para almacenar el usuario encontrado
    var usuarioEncontrado = null;
    
    // Iterar sobre la lista de usuarios y buscar la cédula
    for (var i = 0; i < usuarios.length; i++) {
        if (usuarios[i].ruc === cedula) {
            usuarioEncontrado = usuarios[i];
            break; // Terminar el bucle una vez que se encuentre el usuario
        }
    }
    

    var divUsuarioNoEncontrado = document.getElementById("mensajeUsuarioNoEncontrado");

    if (usuarioEncontrado) {
        console.log("Usuario encontrado:", usuarioEncontrado);
        divUsuarioNoEncontrado.textContent = "Proveedor registrado en la base de datos.";
        divUsuarioNoEncontrado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        divUsuarioNoEncontrado.classList.remove("alert-danger"); // Remover la clase de alerta roja
        divUsuarioNoEncontrado.classList.add("alert-success"); // Agregar la clase de alerta verde
        llenarCampos(usuarioEncontrado);
    } else {
        divUsuarioNoEncontrado.textContent = "Proveedor no encontrado en la base de datos... Ingresa los datos del proveedor";
        divUsuarioNoEncontrado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        divUsuarioNoEncontrado.classList.remove("alert-success"); // Remover la clase de alerta verde
        divUsuarioNoEncontrado.classList.add("alert-danger"); // Agregar la clase de alerta roja
        camposVacios();
    }
    
    divUsuarioNoEncontrado.style.display = "block"; // Mostrar el mensaje de usuario no encontrado

    
}

function llenarCampos(proveedor) {
    document.getElementById("nombre").value = proveedor.nombre ? proveedor.nombre : '';
    document.getElementById("ciudad").value = proveedor.ciudad ? proveedor.ciudad : '';
    document.getElementById("direccion").value = proveedor.direccion ? proveedor.direccion : '';
    document.getElementById("contacto").value = proveedor.contacto ? proveedor.contacto : '';
    document.getElementById("email").value = proveedor.email ? proveedor.email : '';
    document.getElementById("celular").value = proveedor.telefono ? proveedor.telefono : '';
    document.getElementById("numeroFactura").value = proveedor.numeroFactura ? proveedor.numeroFactura : '';
}

function camposVacios() {
    document.getElementById("nombre").value = "";
    document.getElementById("ciudad").value = "";
    document.getElementById("direccion").value = "";
    document.getElementById("contacto").value = "";
    document.getElementById("email").value = "";
    document.getElementById("celular").value = "";
    document.getElementById("numeroFactura").value = "";
    // Otros campos
}

// Obtener elementos del DOM
var btnMostrarModal = document.getElementById("mostrarModal");
var modalFondo = document.getElementById("modalFondoBusqueda");
var modal = document.getElementById("miModalBusqueda");
var btnCerrarModal = document.getElementById("cerrar-modal");
var inputBuscador = document.getElementById("buscadorModal");

// Cerrar el modal al hacer clic en la "x" o fuera del modal
$('.cerrar-modal, #modalFondoBusqueda').on('click', function () {
    $('#modalFondoBusqueda').fadeOut();
    $('#miModalBusqueda').fadeOut();
});

// Mostrar modal al hacer clic en el botón
btnMostrarModal.addEventListener("click", function() {
    modalFondo.style.display = "block";
    modal.style.display = "block";
});

document.addEventListener("keyup", e => {
    if (e.target.matches("#buscador")) {
        if (e.key === "Escape") e.target.value = "";

        const articulos = document.querySelectorAll(".articulo");
        const filtro = e.target.value.toLowerCase();
        let productosEncontrados = false;

        articulos.forEach(articulo => {
            const contenido = articulo.textContent.toLowerCase();
            if (contenido.includes(filtro)) {
                articulo.classList.remove("filtro");
                productosEncontrados = true;
            } else {
                articulo.classList.add("filtro");
            }
        });

        // Mostrar u ocultar el mensaje de "No se encontraron productos"
        const mensajeNoProductos = document.getElementById("mensajeNoProductos");
        if (productosEncontrados) {
            mensajeNoProductos.style.display = "none";
        } else {
            mensajeNoProductos.style.display = "block";
        }
    }
});





// Seleccionar todos los elementos con la clase "agregar-producto"
var botonesAgregarProducto = document.querySelectorAll(".agregar-producto");

// Iterar sobre cada botón y agregar un manejador de eventos click
botonesAgregarProducto.forEach(function(boton) {
    boton.addEventListener("click", function() {
        // Obtener el ID del producto del atributo data-producto-id
        var productoId = this.getAttribute("data-producto-id");


        // Obtener el color seleccionado
        var colorSelect = document.getElementById('select-color-' + productoId);
        var colorSeleccionado = colorSelect.options[colorSelect.selectedIndex].text;
        console.log("color ",colorSeleccionado);

        // Obtener la cantidad seleccionada
        var stockSelect = document.getElementById('select-stock-' + productoId);
        var cantidadSeleccionada = stockSelect.options[stockSelect.selectedIndex].text;
        console.log("cantidad: ", cantidadSeleccionada);

        // Obtener el código de artículo seleccionado
        var codigoArticulo = colorSelect.options[colorSelect.selectedIndex].dataset.codigoArticulo;
        console.log("codigo articulo: ", codigoArticulo);

        // Obtener los IDs de productos guardados previamente del localStorage
        var productosGuardados = localStorage.getItem("productos_facturacion");
        
        // Convertir la cadena de productos guardados en un arreglo (si existe)
        var productosFacturacion = productosGuardados ? JSON.parse(productosGuardados) : [];

        
        // Verificar si el producto ya está guardado
        var productoExistente = productosFacturacion.find(function(producto) {
            return producto.codigo === codigoArticulo;
        });

        if (productoExistente) {
            // Si el producto ya existe, actualizar su color y cantidad
            productoExistente.color = colorSeleccionado;
            productoExistente.cantidad = cantidadSeleccionada;
        } else {
            // Si el producto no existe, añadirlo a la lista
            productosFacturacion.push({
                id: productoId,
                codigo: codigoArticulo,
                color: colorSeleccionado,
                cantidad: cantidadSeleccionada
            });
        }
     
        // Guardar la lista actualizada en el localStorage
        localStorage.setItem("productos_facturacion", JSON.stringify(productosFacturacion));

        actualizarTabla();
     
        // Cerrar el modal
        $('#modalFondoBusqueda').fadeOut();
        $('#miModalBusqueda').fadeOut();
    });
});

function actualizarTabla(){
    // Obtener los datos del localStorage
    var productosGuardados = localStorage.getItem("productos_facturacion");
    var productosFacturacion = productosGuardados ? JSON.parse(productosGuardados) : [];


    // Obtén el token CSRF del cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Busca el nombre del cookie
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');
    var descuento = document.getElementById("descuento").value;


    $.ajax({
        url: 'producto',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': csrftoken  // Agrega el token CSRF al encabezado
        },
        data: JSON.stringify({ productosFacturacion: productosFacturacion, descuento: descuento }),
        success: function(response) {
            var subtotal = response.subtotal;
            console.log('Datos enviados correctamente 3');
            // Obtén la tabla tbody donde deseas agregar los productos
           var tbody = $('#productos-tbody');
            // Limpia cualquier contenido previo
           tbody.empty();

            // Itera sobre los productos y agrega cada uno como una fila a la tabla
            response.productos.forEach(function(producto) {
                var row = $('<tr>');
                row.append('<td><b>' +producto.codigo + '</b></td>');
                row.append('<td>' +producto.modelo+' '+ producto.detalle + '</td>');
                row.append('<td>' + producto.color + '</td>');
                row.append('<td>' + producto.cantidad + '</td>');
                //row.append('<th scope="row">' + producto.codigo + '</th>');
                row.append('<td>' + producto.precio + '</td>');
                row.append('<td style="text-align: right;">' + producto.preciot + '</td>');
                row.append('<td> <button class="eliminar" onclick="eliminarProducto(this)" data-id="' + producto.id + '"><i class="fa-solid fa-trash"></i></button> </td>');
                tbody.append(row);
            });

            // Agregar fila para el subtotal
            var rowSubtotal = $('<tr>');
            rowSubtotal.append('<td></td>');
            rowSubtotal.append('<td></td>');
            rowSubtotal.append('<td></td>');
            rowSubtotal.append('<td></td>');
            rowSubtotal.append('<td><b>Subtotal</b></td>');
            rowSubtotal.append('<td><b>'+subtotal+'</b></td>');
            tbody.append(rowSubtotal);


            var rowDescuento = $('<tr>');
            rowDescuento.append('<td></td>');
            rowDescuento.append('<td></td>');
            rowDescuento.append('<td></td>');
            rowDescuento.append('<td></td>');
            rowDescuento.append('<td>Descuento ('+response.porcentajeDescuento+'%)</td>');
            rowDescuento.append('<td>'+response.descuento+'</td>');
            tbody.append(rowDescuento);

            var rowSubtotalD = $('<tr>');
            rowSubtotalD.append('<td></td>');
            rowSubtotalD.append('<td></td>');
            rowSubtotalD.append('<td></td>');
            rowSubtotalD.append('<td></td>');
            rowSubtotalD.append('<td>Sub/Descuento</td>');
            rowSubtotalD.append('<td>'+response.subtotalD+'</td>');
            tbody.append(rowSubtotalD);

            var rowIva = $('<tr>');
            rowIva.append('<td></td>');
            rowIva.append('<td></td>');
            rowIva.append('<td></td>');
            rowIva.append('<td></td>');
            rowIva.append('<td>Iva ('+response.porcentaje+'%)</td>');
            rowIva.append('<td>'+response.iva+'</td>');
            tbody.append(rowIva);

            // Calcular el total (puedes agregar más lógica aquí si es necesario)

            var rowTotal = $('<tr>');
            rowTotal.append('<td></td>');
            rowTotal.append('<td>Peso de la compra: <b>'+response.peso+'Kg</b></td>');
            rowTotal.append('<td></td>');
            rowTotal.append('<td></td>');
            rowTotal.append('<td><b>Total</b></td>');
            rowTotal.append('<td><b>'+response.total+'</b></td>');
            tbody.append(rowTotal);

        },
        error: function(xhr, status, error) {
            console.error('Error al enviar los datos al servidor: 4', error);
            
        }
    });
    
    
}


// Agregar controlador de eventos para el botón eliminar
$('#tabla_productos').on('click', '.eliminar', function() {
    var id = $(this).data('id');
    eliminarProducto(id);
    $(this).closest('tr').remove();
});




function enviarFormularioConLocalStorage() {
    // Recuperar los productos guardados del localStorage
    var productosGuardados = localStorage.getItem("productos_facturacion");
     // Obtener el formulario
     var formulario = document.getElementById('miFormulario');

     var camposFormulario = formulario.elements;

     var tipoPagoSelect = document.getElementById('tipoPago');

    // Obtener el valor seleccionado
    var tipoPagoSeleccionado = tipoPagoSelect.value;

    // Verificar si hay productos guardados en el localStorage
    if (productosGuardados) {
       


        // Verificar si el formulario está lleno
        var formularioLleno = true;
        
        for (var i = 0; i < camposFormulario.length; i++) {
            var campo = camposFormulario[i];
            // Verificar si el campo tiene un valor (excluyendo campos ocultos y botones)
            if (campo.type !== 'hidden' && campo.type !== 'button' && campo.value === '') {
                formularioLleno = false;
                break;
            }
            // Verificar si es un selector y tiene una opción seleccionada
            if ((campo.type === 'select-one' || campo.type === 'select-multiple') && campo.selectedIndex === -1) {
                formularioLleno = false;
                break;
            }
        }

        if (formularioLleno) {
            // Preguntar al usuario si desea enviar el formulario
            var confirmacion = confirm('¿Estás seguro de que deseas generar la venta?');
            if (confirmacion) {
                

                // Crear un campo oculto para los productos y agregarlo al formulario
                var campoProductos = document.createElement('input');
                campoProductos.type = 'hidden';
                campoProductos.name = 'productos_facturacion';
                campoProductos.value = productosGuardados;
                formulario.appendChild(campoProductos);

                // Crear un campo oculto para tipo pago
                var campoTipoPago = document.createElement('input');
                campoTipoPago.type = 'hidden';
                campoTipoPago.name = 'tipoPago';
                campoTipoPago.value = tipoPagoSeleccionado;
                formulario.appendChild(campoTipoPago);

                // Comprobar si el tipo de pago es 'Cheque'
                if (tipoPagoSeleccionado === 'Cheque') {
                    var numeroChequeInput = document.getElementById('numeroChequeInput');
                    // Crear un campo oculto para tipo pago
                    var numeroCheque = document.createElement('input');
                    numeroCheque.type = 'hidden';
                    numeroCheque.name = 'numeroCheque';
                    numeroCheque.value = numeroChequeInput.value;
                    formulario.appendChild(numeroCheque);

                    //para el nombre del banco
                    var bancoSelect = document.getElementById('banco');

                    // Obtener el valor seleccionado
                    var bancoSeleccionado = bancoSelect.value;

                    if (bancoSeleccionado === 'Otro') {
                        var otroBanco = document.getElementById('otroBanco');

                        var nombreBanco = document.createElement('input');
                        nombreBanco.type = 'hidden';
                        nombreBanco.name = 'nombreBanco';
                        nombreBanco.value = otroBanco.value;
                        formulario.appendChild(nombreBanco);
                    }else{
                        // Crear un campo oculto para tipo pago
                        var nombreBanco = document.createElement('input');
                        nombreBanco.type = 'hidden';
                        nombreBanco.name = 'nombreBanco';
                        nombreBanco.value = bancoSeleccionado;
                        formulario.appendChild(nombreBanco);
                    }
                } if (tipoPagoSeleccionado === 'Combinado (Crédito/Contado)'){
                    // Obtener referencias a los elementos
                    const checkbox1 = document.getElementById('check1');
                    const checkbox2 = document.getElementById('check2');
                    const checkbox3 = document.getElementById('check3');

                    const input1 = document.getElementById('input1');
                    const input2 = document.getElementById('input2');
                    const input3 = document.getElementById('input3');

                    const seleccionados = [];
    
                    if (checkbox1.checked) {
                        seleccionados.push({
                            tipo: 'Efectivo',
                            valor: input1.value
                        });
                    }
                    
                    if (checkbox2.checked) {
                        seleccionados.push({
                            tipo: 'Tarjeta de Crédito',
                            valor: input2.value
                        });
                    }
                    
                    if (checkbox3.checked) {
                        seleccionados.push({
                            tipo: 'Cheque',
                            valor: input3.value
                        });
                    }

                    // Serializar el array de objetos a formato JSON
                    const combinadosJson = JSON.stringify(seleccionados);

                    var combinados = document.createElement('input');
                    combinados.type = 'hidden';
                    combinados.name = 'combinados';
                    combinados.value = combinadosJson;
                    formulario.appendChild(combinados);

                } else {
                    var numeroCheque = document.createElement('input');
                    numeroCheque.type = 'hidden';
                    numeroCheque.name = 'numeroCheque';
                    numeroCheque.value = 'x';
                    formulario.appendChild(numeroCheque);
                }


                // Obtener los datos de los otros campos del formulario y agregarlos al formulario
                var formData = new FormData(formulario);
                for (var pair of formData.entries()) {
                    if (pair[0] !== 'productos_facturacion') {
                        var campo = document.createElement('input');
                        campo.type = 'hidden';
                        campo.name = pair[0];
                        campo.value = pair[1];
                        formulario.appendChild(campo);
                    }
                }

                // Enviar el formulario
                formulario.submit();
            }
        } else {
            alert('Por favor, completa todos los campos del formulario antes de generar la venta.');
        }
    }else{
        alert('Aún no se han agregado productos. Asegúrate de agregar productos para generar una nota de venta.');
    }

    
}

// Agregar un controlador de eventos al botón limpiar
document.querySelector('.cancelar').addEventListener('click', function() {
    // Confirmar la acción antes de eliminar
    var confirmacion = confirm("¿Estás seguro de que deseas limpiar la actual pantalla?");

    // Verificar la respuesta del usuario
    if (confirmacion) {
        // Eliminar el elemento del localStorage
        localStorage.removeItem("productos_facturacion");
        console.log("LocalStorage 'productos_facturacion' eliminado.");
        // Recargar la página
        location.reload();
    } else {
        console.log("Cancelado.");
    }
});


function eliminarProducto(button) {
    
    var productoId = button.getAttribute('data-id');
    console.log('ID del producto a eliminar:', productoId);

    
    // Obtener los productos guardados del localStorage
    var productosGuardados = localStorage.getItem("productos_facturacion");

    // Verificar si hay productos guardados
    if (productosGuardados) {
        // Convertir los productos guardados en un arreglo de JavaScript
        var productosFacturacion = JSON.parse(productosGuardados);

        // Encontrar el índice del producto con el ID especificado
        var indiceProducto = productosFacturacion.findIndex(function(producto) {
            return producto.id === productoId;
        });

        // Si se encontró el producto, eliminarlo del arreglo
        if (indiceProducto !== -1) {
            productosFacturacion.splice(indiceProducto, 1);

            // Actualizar el localStorage con la lista de productos actualizada
            localStorage.setItem("productos_facturacion", JSON.stringify(productosFacturacion));
            
            var productosArray = JSON.parse(productosGuardados);

            // Determinar si el último elemento se eliminará
            // Hago esta validacion porque si se quiere eliminar el ultimo elemto y mando a actualizarTabla(); no se realizara por el motivo de 
            // que el array esta vacio, asi que si solo hay un elemento y este se requiere eliminar, simplemente limpio la tabla.
            if (productosArray.length === 1) {
                console.log("Este es el último elemento que se eliminará");
                 // Obtén la tabla tbody donde deseas agregar los productos
                var tbody = $('#productos-tbody');
                // Limpia cualquier contenido previo
                tbody.empty();
            } else {
                console.log("No es el último elemento que se eliminará");
                actualizarTabla();
            }

            
        } else {
            console.log('El producto con ID', productoId, 'no se encontró.');
        }
    } else {
        console.log('No hay productos guardados en el localStorage.');
    }

}


//************MODAL BUSCAR CLIENTE **********/

function openModalProveedor() {
    document.getElementById('modalFondoBusqueda').style.display = 'block';
    document.getElementById('modalContenidoCliente').style.display = 'block';
}

function closeModalProveedor() {
    document.getElementById('modalFondoBusqueda').style.display = 'none';
    document.getElementById('modalContenidoCliente').style.display = 'none';

    //verifico si se han llenado todos los campos para poner un alert de campos llenos
    var ruc = document.getElementById("ruc").value;
    var nombre = document.getElementById("nombre").value;
    var ciudad = document.getElementById("ciudad").value;
    var direccion = document.getElementById("direccion").value;
    var contacto = document.getElementById("contacto").value;
    var email = document.getElementById("email").value;
    var celular = document.getElementById("celular").value;
    var numeroFactura = document.getElementById("numeroFactura").value;
    // Verificar si los campos están llenos
    var mensajeUsuarioIngresado = document.getElementById("mensajeUsuarioIngresado");
    var datosCliente = document.getElementById("datosCliente");

    if (ruc && nombre && ciudad && direccion) {
        mensajeUsuarioIngresado.textContent = "Los datos del Proveedor se han ingresado";
        mensajeUsuarioIngresado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        mensajeUsuarioIngresado.classList.remove("alert-danger"); // Remover la clase de alerta roja
        mensajeUsuarioIngresado.classList.add("alert-success"); // Agregar la clase de alerta verde

         // Mostrar los datos del cliente en un nuevo div
         datosCliente.innerHTML = "<h6>Artículos proporcionados por: </h6><br>" +
         "<strong>" +nombre + "</strong> - "+ ruc +"<br>" +
         "Dirección: " + ciudad +" - "+direccion +"<br>"+
         "Contacto: "+contacto +" - "+email+" - "+celular+"<br>"+
          "# Factura adquirida: " + numeroFactura;
        
    } else {
        mensajeUsuarioIngresado.textContent = "Los datos del Proveedor no están completos, puede que te falte ingresar un campo aún.";
        mensajeUsuarioIngresado.classList.remove("alert-success"); // Remover la clase de alerta amarilla
        mensajeUsuarioIngresado.classList.remove("alert-danger"); // Remover la clase de alerta roja
        mensajeUsuarioIngresado.classList.add("alert-warning"); // Agregar la clase de alerta verde
        datosCliente.innerHTML = "";
    }
    actualizarTabla();


}

// Para evitar que el clic en el modal contenedor cierre el modal
document.getElementById('modalContenidoCliente').addEventListener('click', function(event) {
    event.stopPropagation();
});

// Para cerrar el modal si se hace clic fuera de él
document.getElementById('modalFondoBusqueda').addEventListener('click', function() {
    closeModalProveedor();
});





