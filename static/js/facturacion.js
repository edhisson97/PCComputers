window.onload = function() {
    // Llama a tu función aquí
    actualizarTabla();
};

var selects = document.querySelectorAll('.select-color');
        selects.forEach(function(select) {
            // Llenar select-stock inicialmente basado en el valor predeterminado de select-color
            updateStockSelect(select);

            select.addEventListener('change', function() {
                updateStockSelect(this);
            });
        });

        function updateStockSelect(select) {
            var selectedOption = select.options[select.selectedIndex];
            var stock = parseInt(selectedOption.getAttribute('data-stock'));

            var stockSelectId = 'select-stock-' + select.id.split('-')[2];
            var stockSelect = document.getElementById(stockSelectId);
            stockSelect.innerHTML = ''; // Limpiar opciones existentes

            for (var i = 1; i <= stock; i++) {
                var option = document.createElement('option');
                option.text = i;
                option.value = i;
                stockSelect.appendChild(option);
            }
        }

function buscarCliente() {
    var cedula = document.getElementById("cedula").value;
    var usuariosString = document.getElementById("cedula").getAttribute("data-usuarios");
    var usuarios = JSON.parse(usuariosString);
    
    // Variable para almacenar el usuario encontrado
    var usuarioEncontrado = null;
    
    // Iterar sobre la lista de usuarios y buscar la cédula
    for (var i = 0; i < usuarios.length; i++) {
        if (usuarios[i].cedula === cedula) {
            usuarioEncontrado = usuarios[i];
            break; // Terminar el bucle una vez que se encuentre el usuario
        }
    }
    

    var divUsuarioNoEncontrado = document.getElementById("mensajeUsuarioNoEncontrado");

    if (usuarioEncontrado) {
        console.log("Usuario encontrado:", usuarioEncontrado);
        divUsuarioNoEncontrado.textContent = "Usuario registrado en la base de datos.";
        divUsuarioNoEncontrado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        divUsuarioNoEncontrado.classList.remove("alert-danger"); // Remover la clase de alerta roja
        divUsuarioNoEncontrado.classList.add("alert-success"); // Agregar la clase de alerta verde
        llenarCampos(usuarioEncontrado);
    } else {
        divUsuarioNoEncontrado.textContent = "Usuario no encontrado en la base de datos... Ingresa los datos del usuario";
        divUsuarioNoEncontrado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        divUsuarioNoEncontrado.classList.remove("alert-success"); // Remover la clase de alerta verde
        divUsuarioNoEncontrado.classList.add("alert-danger"); // Agregar la clase de alerta roja
        camposVacios();
    }
    
    divUsuarioNoEncontrado.style.display = "block"; // Mostrar el mensaje de usuario no encontrado

    
}

function llenarCampos(cliente) {
    document.getElementById("nombre").value = cliente.nombre ? cliente.nombre : '';
    document.getElementById("apellidos").value = cliente.apellidos ? cliente.apellidos : '';
    document.getElementById("email").value = cliente.email ? cliente.email : '';
    document.getElementById("celular").value = cliente.celular ? cliente.celular : '';
    document.getElementById("ciudad").value = cliente.ciudad ? cliente.ciudad : '';
    document.getElementById("direccion").value = cliente.direccion ? cliente.direccion : '';
    document.getElementById("direccionEnvio").value = cliente.direccionEnvio ? cliente.direccionEnvio : cliente.direccion;
}

function camposVacios() {
    document.getElementById("nombre").value = "";
    document.getElementById("apellidos").value = "";
    document.getElementById("email").value = "";
    document.getElementById("celular").value = "";
    document.getElementById("ciudad").value = "";
    document.getElementById("direccion").value = "";
    document.getElementById("direccionEnvio").value = "";
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

function openModalCliente() {
    document.getElementById('modalFondoBusqueda').style.display = 'block';
    document.getElementById('modalContenidoCliente').style.display = 'block';
}

function closeModalCliente() {
    document.getElementById('modalFondoBusqueda').style.display = 'none';
    document.getElementById('modalContenidoCliente').style.display = 'none';

    //verifico si se han llenado todos los campos para poner un alert de campos llenos
    var cedula = document.getElementById("cedula").value;
    var celular = document.getElementById("celular").value;
    var nombre = document.getElementById("nombre").value;
    var apellidos = document.getElementById("apellidos").value;
    var ciudad = document.getElementById("ciudad").value;
    var direccion = document.getElementById("direccion").value;
    var direccionEnvio = document.getElementById("direccionEnvio").value;
    var email = document.getElementById("email").value;
    // Verificar si los campos están llenos
    var mensajeUsuarioIngresado = document.getElementById("mensajeUsuarioIngresado");
    var datosCliente = document.getElementById("datosCliente");

    if (cedula && celular && nombre && apellidos && ciudad && direccion && email) {
        mensajeUsuarioIngresado.textContent = "Los datos del cliente se han ingresado";
        mensajeUsuarioIngresado.classList.remove("alert-warning"); // Remover la clase de alerta amarilla
        mensajeUsuarioIngresado.classList.remove("alert-danger"); // Remover la clase de alerta roja
        mensajeUsuarioIngresado.classList.add("alert-success"); // Agregar la clase de alerta verde

         // Mostrar los datos del cliente en un nuevo div
         datosCliente.innerHTML = "<h6>Factura a favor de: </h6><br>" +
         "<strong>" + apellidos + " " +nombre + "</strong> - "+ cedula +"<br>" +
         "Dirección: " + ciudad +" / "+direccion +"<br>"+
         "Envío: "+direccionEnvio +"<br>"+
          email;
        
    } else {
        mensajeUsuarioIngresado.textContent = "Los datos del cliente no están completos, puede que te falte ingresar un campo aún.";
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
    closeModalCliente();
});


//************validar descuento hasta 10% ********
function validarDescuento() {
    var descuentoInput = document.getElementById("descuento");
    var descuento = parseFloat(descuentoInput.value);
    var errorMsg = document.getElementById("error-msg");
    
    if (descuento > 10) {
        errorMsg.style.display = "block";
        descuentoInput.value = 10; // Si es mayor que 10, establecerlo como 10
    } else {
        errorMsg.style.display = "none";
    }
}

//***************consumidor final */

function autocompletarCampos() {
    var tipo = document.getElementById("tipo").value;
    if (tipo === "consumidor") {
        
        // Aquí puedes establecer los valores predeterminados para los campos del consumidor final
        document.getElementById("nombre").value = "Consumidor";
        document.getElementById("apellidos").value = "Final";
        document.getElementById("ciudad").value = "Ciudad";
        document.getElementById("email").value = "email@consumidor.com";
        document.getElementById("direccion").value = "Dirección Consumidor";
        document.getElementById("direccionEnvio").value = "Dirección de envío Consumidor";
        document.getElementById("cedula").value = "0000000001";
        document.getElementById("celular").value = "0000000000";
        
    } else {
        // Si se selecciona otro tipo, puedes borrar los valores de los campos del consumidor final
        document.getElementById("nombre").value = "";
        document.getElementById("apellidos").value = "";
        document.getElementById("ciudad").value = "";
        document.getElementById("email").value = "";
        document.getElementById("direccion").value = "";
        document.getElementById("direccionEnvio").value = "";
        document.getElementById("cedula").value = "";
        document.getElementById("celular").value = "";
    }
}

/*****numero de cheque */
function mostrarNumeroCheque() {
    var tipoPago = document.getElementById("tipoPago").value;
    var numeroChequeDiv = document.getElementById("numeroCheque");

    // Si se selecciona "Cheque", muestra el campo para el número de cheque, de lo contrario, ocúltalo
    if (tipoPago === "Cheque") {
        numeroChequeDiv.style.display = "block";
    } else {
        numeroChequeDiv.style.display = "none";
    }
}
