// Obtener referencia al botón del carrito y la notificación
var carritoBtn = document.getElementById('carrito-btn');
var notificacion = document.getElementById('carrito-notificacion');

// Función para obtener la cantidad de productos en el carrito desde el localStorage
function obtenerCantidadEnCarrito() {
    var carrito = JSON.parse(localStorage.getItem("storedProducts")) || [];
    return carrito.length;
}

// Función para actualizar la notificación del carrito
function actualizarNotificacionCarrito() {
    var cantidadEnCarrito = obtenerCantidadEnCarrito();
    notificacion.innerText = cantidadEnCarrito;
}

// Actualizar la notificación al cargar la página
actualizarNotificacionCarrito();


//*************CARIITO COMPRAS *******************/
document.addEventListener('DOMContentLoaded', function() {
    var carritoBtn = document.getElementById('carrito-btn');
    var carritoSidebar = document.getElementById('carrito-sidebar');
    var cerrarCarritoBtn = document.getElementById('cerrar-carrito');
    var fondoCarrito = document.getElementById('fondo-carrito');
    var cantidad = 1;

    carritoBtn.addEventListener('click', function() {
         // Actualiza el contenido del carrito antes de mostrarlo
        var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];
        actualizarContenidoCarrito(storedProducts, cantidad);
        // Muestra el carrito
        carritoSidebar.style.right = '0';
        document.body.classList.add('carrito-abierto');
    });

    cerrarCarritoBtn.addEventListener('click', function() {
        carritoSidebar.style.right = '-300px';
        document.body.classList.remove('carrito-abierto');
    });

    fondoCarrito.addEventListener('click', function() {
        carritoSidebar.style.right = '-300px';
        document.body.classList.remove('carrito-abierto');
    });


});


document.addEventListener('DOMContentLoaded', function() {
    // Agregar un evento de clic al enlace
    document.getElementById('btnIrAPagar').addEventListener('click', function() {
      // Obtener datos de localStorage
      var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];

      // Hacer algo con los datos si es necesario

      // Construir la URL con los datos y redirigir
      var url = '/carrito?storedProducts=' + encodeURIComponent(JSON.stringify(storedProducts));
      window.location.href = url;
    });
  });


/**********Guardo los id de los productos agregados al carrito ******/
$(document).ready(function() {

    // Al cargar la página, verifica el estado del carrito y actualiza los botones
    updateCartButtons();

    $(".comprar").on("click", function() {
        var button = $(this);
        var productId = button.data("product-id");
        var productMarca = button.data("product-marca");
        var productModelo = button.data("product-modelo");

        // Obtiene el arreglo actual de IDs de productos de localStorage
        var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];

        // Verifica si el producto ya está en el carrito
        var isInCart = storedProducts.includes(productId);

        var carritoSidebar = document.getElementById('carrito-sidebar');

        var cantidad = 1;

        if (!isInCart) {
            // Si no está en el carrito, agrégalo
            storedProducts.push(productId);
            localStorage.setItem("storedProducts", JSON.stringify(storedProducts));

            // Cambia el texto del botón a "Ver Carrito"
            button.text("Ver en carrito").addClass("ver-carrito");
            
            // Muestra un mensaje o realiza otras acciones según sea necesario
            showNotification("Producto "+productMarca+" "+productModelo+" añadido al carrito de compras.");
            // Actualizar la notificación al cargar la página
            actualizarNotificacionCarrito();
        } else {
            // Si ya está en el carrito, puedes manejarlo de alguna manera (mostrar un mensaje, por ejemplo)
            //showNotification("El producto ya está en el carrito.");
            actualizarContenidoCarrito(storedProducts, cantidad);
            // Muestra el carrito
            carritoSidebar.style.right = '0';
            document.body.classList.add('carrito-abierto');
        }

    });

    $(document).on("click", ".eliminar-producto", function() {
        console.log("Clic en el botón de eliminar");
        var button = $(this);
        console.log(button);
        var productId = button.data("producto-id");
        console.log("Variable id: " + productId);
        var cantidad = 1;
        
    
        // Obtiene el arreglo actual de IDs de productos de localStorage
        var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];

        // Filtra el arreglo para excluir el producto que se va a eliminar
        storedProducts = storedProducts.filter(function(id) {
            return id !== productId;
        });

        // Actualiza el localStorage con el nuevo arreglo de productos
        localStorage.setItem("storedProducts", JSON.stringify(storedProducts));
        //localStorage.setItem("storedProductsColor", JSON.stringify(storedProductsColor));
    
        // Actualiza el contenido del carrito
        actualizarContenidoCarrito(storedProducts,cantidad);
        updateCartButtons();
    
    
        // Puedes realizar otras acciones según sea necesario
        showNotification("Producto eliminado del carrito.");
        // Actualizar la notificación al cargar la página
        actualizarNotificacionCarrito();

    });

    $(document).on("click", ".btnIrAPagar", function(event) {
        event.preventDefault(); // Evitar la acción predeterminada del enlace
    
        console.log("Clic en el botón seguir con la compra");
    
        // Obtener datos de localStorage
        var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];
    
        // Hacer algo con los datos si es necesario
    
        // Construir la URL con los datos y redirigir
        var url = '/carrito?storedProducts=' + encodeURIComponent(JSON.stringify(storedProducts));
        
        // Redirigir a la nueva URL
        window.location.href = url;
    });


    // Función para actualizar los botones según el estado del carrito
    function updateCartButtons() {
        // Obtiene el arreglo actual de IDs de productos de localStorage
        var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];

        // Itera sobre los botones y cambia el texto según estén en el carrito o no
        $(".comprar").each(function() {
            var button = $(this);
            var productId = button.data("product-id");

            if (storedProducts.includes(productId)) {
                button.text("Ver en carrito").addClass("ver-carrito").delay(10).queue(function(next) {
                    $(this).css({"background-color": "#575656"});
                    next();
                });
            } else {
                button.text("Comprar").addClass("comprar").delay(10).queue(function(next) {
                    $(this).css({"background-color": "#c53c32"});
                    next();
                });
            }
        });
    }

});



/***para llamar a notificaciones *********/

function showNotification(message) {
    var notification = document.getElementById("notification");
    var notificationText = document.getElementById("notification-text");

    notificationText.textContent = message;
    notification.classList.add("visible");

    setTimeout(function() {
        notification.classList.remove("visible");
    }, 5000); // Oculta la notificación después de 3 segundos (ajusta según tus necesidades)
}

//******************para actualizar el carrito */

// Obtén la referencia al contenedor de los elementos del carrito
var carritoItemsContainer = document.getElementById('carrito-items-container');

// Función para actualizar el contenido del carrito
function actualizarContenidoCarrito(storedProducts,cantidad) {
    // Realiza una solicitud AJAX para obtener los datos actualizados del carrito
    var xhr = new XMLHttpRequest();
    // Incluye los productos almacenados como parámetros en la URL
    var url = '/obtener_carrito/?storedProducts=' + encodeURIComponent(JSON.stringify(storedProducts)) + '&cantidad=' + cantidad;
    
    xhr.open('GET', url, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Actualiza el contenido del carrito
            carritoItemsContainer.innerHTML = xhr.responseText;
        }
    };

    xhr.send();
    // Actualizar la notificación al cargar la página
    actualizarNotificacionCarrito();
}
