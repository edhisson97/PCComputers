window.onload = function() {
    // Llama a tu función aquí
    actualizarTabla();
};

document.addEventListener("DOMContentLoaded", function () {
    // Verifica si la URL actual es "/operacion/stock"
    if (window.location.pathname === "/operacion/stock") {
        actualizarTablaStock();
    }

    // Obtener elementos del DOM
    var btnMostrarModal2 = document.getElementById("mostrarModal2");
    var modalFondo2 = document.getElementById("modalFondoBusqueda2");
    var modal2 = document.getElementById("miModalBusqueda2");
    var btnCerrarModal2 = modal2.querySelector(".cerrar-modal"); // Busca la "X" dentro del modal

    // Verificar si el botón existe antes de agregar eventos
    if (btnMostrarModal2) {
        btnMostrarModal2.addEventListener("click", function () {
            console.log("Botón presionado: mostrando modal 2"); // Debugging
            modalFondo2.style.display = "block";
            modal2.style.display = "block";
        });
    } else {
        console.error("El botón para abrir el modal 2 no se encontró en el DOM.");
    }

    // Cerrar el modal al hacer clic en la "X"
    if (btnCerrarModal2) {
        btnCerrarModal2.addEventListener("click", function () {
            console.log("Cerrando modal 2"); // Debugging
            modalFondo2.style.display = "none";
            modal2.style.display = "none";
        });
    }

    // Cerrar el modal al hacer clic fuera de él
    modalFondo2.addEventListener("click", function () {
        console.log("Cerrando modal 2 por fondo"); // Debugging
        modalFondo2.style.display = "none";
        modal2.style.display = "none";
    });
});

function buscarProveedor() {
    const inputBuscar = document.getElementById("buscar");
    const query = inputBuscar.value.trim().toLowerCase();
    const proveedoresString = inputBuscar.getAttribute("data-proveedores");
    const proveedores = JSON.parse(proveedoresString);
    const coincidenciasDiv = document.getElementById("listaCoincidencias");
    const mensajeNoEncontrado = document.getElementById("mensajeUsuarioNoEncontrado");

    coincidenciasDiv.innerHTML = '';
    coincidenciasDiv.style.display = 'none';

    if (query === '') {
        camposVacios();
        mensajeNoEncontrado.style.display = "none";
        return;
    }

    const coincidencias = proveedores.filter(proveedor =>
        proveedor.ruc.toLowerCase().includes(query) ||
        proveedor.nombre.toLowerCase().includes(query)
    ).slice(0, 3); // máximo 3 resultados

    if (coincidencias.length > 0) {
        coincidencias.forEach(proveedor => {
            const opcion = document.createElement("div");
            opcion.textContent = `${proveedor.nombre} - ${proveedor.ruc}`;
            opcion.style.padding = "8px";
            opcion.style.cursor = "pointer";
            opcion.style.borderBottom = "1px solid #eee";

            opcion.addEventListener("click", () => {
                llenarCampos(proveedor);
                coincidenciasDiv.style.display = "none";
                mensajeNoEncontrado.textContent = "Proveedor registrado en la base de datos.";
                mensajeNoEncontrado.classList.remove("alert-warning", "alert-danger");
                mensajeNoEncontrado.classList.add("alert-success");
                mensajeNoEncontrado.style.display = "block";
                
            });

            coincidenciasDiv.appendChild(opcion);
        });

        coincidenciasDiv.style.display = "block";
        } else {
        camposVacios();
        mensajeNoEncontrado.textContent = "Proveedor no encontrado en la base de datos... Ingresa los datos del proveedor";
        mensajeNoEncontrado.classList.remove("alert-success", "alert-warning");
        mensajeNoEncontrado.classList.add("alert-danger");
        mensajeNoEncontrado.style.display = "block";
    }
} 

function llenarCampos(proveedor) {
    document.getElementById("nombre").value = proveedor.nombre ? proveedor.nombre : '';
    document.getElementById("ciudad").value = proveedor.ciudad ? proveedor.ciudad : '';
    document.getElementById("direccion").value = proveedor.direccion ? proveedor.direccion : '';
    document.getElementById("contacto").value = proveedor.contacto ? proveedor.contacto : '';
    document.getElementById("email").value = proveedor.email ? proveedor.email : '';
    document.getElementById("celular").value = proveedor.telefono ? proveedor.telefono : '';
    document.getElementById("ruc").value = proveedor.ruc ? proveedor.ruc : '';
}

function camposVacios() {
    document.getElementById("nombre").value = "";
    document.getElementById("ciudad").value = "";
    document.getElementById("direccion").value = "";
    document.getElementById("contacto").value = "";
    document.getElementById("email").value = "";
    document.getElementById("celular").value = "";
    document.getElementById("ruc").value = "";
    // Otros campos
}


// Agregar un controlador de eventos al botón limpiar
document.querySelector('.cancelar').addEventListener('click', function() {
    // Confirmar la acción antes de eliminar
    var confirmacion = confirm("¿Estás seguro de que deseas limpiar la actual pantalla?");

    // Verificar la respuesta del usuario
    if (confirmacion) {
        // Eliminar el elemento del localStorage
        localStorage.removeItem("productos_stock");
        console.log("LocalStorage 'productos_facturacion' eliminado.");
        // Recargar la página
        location.reload();
    } else {
        console.log("Cancelado.");
    }
});


//************MODAL BUSCAR PROVEEDOR **********/

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
         "Contacto: "+contacto +" - "+email+" - "+celular+"<br>";
        
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


document.addEventListener("keyup", (e) => {
    if (e.target.matches("#buscador")) {
        if (e.key === "Escape") e.target.value = "";

        const filtro = e.target.value.toLowerCase().trim();
        const articulos = document.querySelectorAll(".articulo");
        let productosEncontrados = false;

        articulos.forEach((articulo) => {
            const nombre = articulo.querySelector(".detalles h3") ? articulo.querySelector(".detalles h3").textContent.toLowerCase() : "";
            const codigoRef = articulo.querySelector(".codigo-referencial p") ? articulo.querySelector(".codigo-referencial p").textContent.toLowerCase() : "";
            const codigoArt = articulo.querySelector(".codigo-articulo p") ? articulo.querySelector(".codigo-articulo p").textContent.toLowerCase() : "";
            
            // Verifica si el filtro está en alguno de los elementos
            if (nombre.includes(filtro) || codigoRef.includes(filtro) || codigoArt.includes(filtro)) {
                articulo.classList.remove("filtro");
                productosEncontrados = true;
            } else {
                articulo.classList.add("filtro");
            }
        });

        // Mostrar mensaje si no se encontraron productos
        const mensajeNoProductos = document.getElementById("mensajeNoProductos");
        mensajeNoProductos.style.display = productosEncontrados ? "none" : "block";
    }
});

// Seleccionar todos los elementos con la clase "agregar-producto"
var botonesAgregarProducto = document.querySelectorAll(".agregar-stock");

// Iterar sobre cada botón y agregar un manejador de eventos click
botonesAgregarProducto.forEach(function(boton) {
    boton.addEventListener("click", function() {
        // Obtener el ID del producto del atributo data-producto-id
        var productoId = this.getAttribute("data-producto-id");

        // Obtener el color seleccionado
        var colorSelect = document.getElementById('select-color-' + productoId);
        var colorSeleccionado = colorSelect.options[colorSelect.selectedIndex].value;

        // Obtener la cantidad seleccionada
        var cantidad = document.getElementById('stock-' + productoId);
        cantidad = cantidad.value;
        //var cantidadSeleccionada = stockSelect.options[stockSelect.selectedIndex].text;

        if (cantidad === "" || cantidad <= 0) {
            alert("Por favor, ingresa una cantidad válida mayor a 0.");
            return; // Detiene la ejecución de la función
        }

        // Obtener los IDs de productos guardados previamente del localStorage
        var productosGuardados = localStorage.getItem("productos_stock");
        
        // Convertir la cadena de productos guardados en un arreglo (si existe)
        var productosStock = productosGuardados ? JSON.parse(productosGuardados) : [];

        
        // Verificar si el producto ya está guardado
        var productoExistente = productosStock.find(function(producto) {
            return producto.color === colorSeleccionado;
        });

        if (productoExistente) {
            // Si el producto ya existe, actualizar su color y cantidad
            productoExistente.cantidad = cantidad;
        } else {
            // Si el producto no existe, añadirlo a la lista
            productosStock.push({
                id: productoId,
                color: colorSeleccionado,
                cantidad: cantidad
            });
        }
     
        // Guardar la lista actualizada en el localStorage
        localStorage.setItem("productos_stock", JSON.stringify(productosStock));

        actualizarTablaStock();
     
        // Cerrar el modal
        $('#modalFondoBusqueda2').fadeOut();
        $('#miModalBusqueda2').fadeOut();
    });
});


function actualizarTablaStock(){
    // Obtener los datos del localStorage
    var productosGuardados = localStorage.getItem("productos_stock");
    var productosStock = productosGuardados ? JSON.parse(productosGuardados) : [];


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


    $.ajax({
        url: '/operacion/actualizarstock',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': csrftoken  // Agrega el token CSRF al encabezado
        },
        data: JSON.stringify({ productosStock: productosStock},),
        success: function(response) {
            console.log('Datos enviados correctamente 3');
            // Obtén la tabla tbody donde deseas agregar los productos
           var tbody = $('#productos-tbody');
            // Limpia cualquier contenido previo
           tbody.empty();

            // Itera sobre los productos y agrega cada uno como una fila a la tabla
            response.productos.forEach(function(producto) {
                var row = $('<tr>');
                row.append('<td><b>' +producto.id + '</b></td>');
                row.append('<td>' +producto.modelo+' '+ producto.detalle + '</td>');
                row.append('<td>' + producto.color + '</td>');
                row.append('<td>' + producto.cantidad + '</td>');
                //row.append('<th scope="row">' + producto.codigo + '</th>');
                row.append('<td>' + producto.precio + '</td>');
                //row.append('<td style="text-align: right;">' + producto.preciot + '</td>');
                row.append('<td> <button class="eliminar" onclick="eliminarProducto(this)" data-id="' + producto.id + '"><i class="fa-solid fa-trash"></i></button> </td>');
                tbody.append(row);
            });


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

function eliminarProducto(button) {
    
    var productoId = button.getAttribute('data-id');
    console.log('ID del producto a eliminar:', productoId);

    // Obtener los productos guardados del localStorage
    var productosGuardados = localStorage.getItem("productos_stock");

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
            localStorage.setItem("productos_stock", JSON.stringify(productosFacturacion));
            
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
                actualizarTablaStock();
            }

            
        } else {
            console.log('El producto con ID', productoId, 'no se encontró.');
        }
    } else {
        console.log('No hay productos guardados en el localStorage.');
    }

}

function validarProveedorYConfirmar() {
    const ruc = document.getElementById("ruc").value.trim();
    const nombre = document.getElementById("nombre").value.trim();
    const ciudad = document.getElementById("ciudad").value.trim();
    const direccion = document.getElementById("direccion").value.trim();
    const contacto = document.getElementById("contacto").value.trim();
    const email = document.getElementById("email").value.trim();
    const celular = document.getElementById("celular").value.trim();
    const numeroFactura = document.getElementById("numeroFactura").value.trim();

    // Lista de campos requeridos
    const camposFaltantes = [];
    if (!ruc) camposFaltantes.push("RUC");
    if (!nombre) camposFaltantes.push("Nombre");
    if (!ciudad) camposFaltantes.push("Ciudad");
    if (!direccion) camposFaltantes.push("Dirección");
    if (!contacto) camposFaltantes.push("Contacto");
    if (!email) camposFaltantes.push("Correo Electrónico");
    if (!celular) camposFaltantes.push("Celular");
    if (!numeroFactura) camposFaltantes.push("Número de Factura");

    // Si hay campos faltantes, mostrar alerta y detener la acción
    if (camposFaltantes.length > 0) {
        alert("Por favor, complete los siguientes campos del proveedor antes de continuar:\n- " + camposFaltantes.join("\n- "));
        return;
    }

    var productosGuardados = localStorage.getItem("productos_stock");
    if (!productosGuardados || productosGuardados.trim() === "[]" || productosGuardados.trim() === "") {
        alert("Debe ingresar productos antes de continuar.");
        return; // Detener la ejecución si no hay productos
    }

    // Mostrar modal de Bootstrap
    let modal = new bootstrap.Modal(document.getElementById("modalConfirmacion"));
    modal.show();

    // Función para confirmar y enviar los datos al servidor
    document.getElementById("btnConfirmarEnvioStock").onclick = function() {
        $('#modalConfirmacion').modal('hide'); // Cerrar el modal
        
        // Obtener token CSRF
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        let csrftoken = getCookie('csrftoken');

        // Construir el objeto con los datos
        const data = {
            proveedor: {
                ruc: ruc,
                nombre: nombre,
                ciudad: ciudad,
                direccion: direccion,
                contacto: contacto,
                email: email,
                celular: celular
            },
            descripcion: descripcion,
            numeroFactura: numeroFactura,
            productos: JSON.parse(productosGuardados)
        };

        // Enviar la solicitud al servidor con Fetch API
        fetch('/operacion/guardar_stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Stock actualizado con éxito.");
                localStorage.removeItem("productos_stock"); // Limpiar el localStorage
                //window.location.reload(); // Recargar la página si es necesario
                // Redirigir a la nueva URL con el ID recibido
                window.location.href = "/operacion/actualizarprecios/" + data.id;
            } else {
                alert("Error: " + (data.error || "No se pudo completar la acción."));
            }
        })
        .catch(error => {
            console.error("Error al enviar los datos:", error);
            alert("Ocurrió un error al intentar actualizar el stock.");
        });
    };
}


