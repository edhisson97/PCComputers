document.addEventListener('DOMContentLoaded', function () {
    var colorCircles = document.querySelectorAll('.color-circle');
    
    colorCircles.forEach(function (colorCircle) {
        colorCircle.addEventListener('click', function () {
            seleccionarColor(colorCircle);
        });
    });
});


//////////////////////////selecciona el primer color de cada producto pero no el stock
document.addEventListener('DOMContentLoaded', function () {
    // Llamada inicial para establecer el stock y la cantidad predeterminados
    var colorCapsules = document.querySelectorAll('.color-capsule');
    colorCapsules.forEach(function (colorCapsule) {
        var defaultColor = colorCapsule.querySelector('.color-circle');
        if (defaultColor) {
            seleccionarColor(defaultColor);
        }
    });
});


function seleccionarColor(colorCircle) {
    // Desmarcar todos los colores
    var colorCapsule = colorCircle.parentElement;
    var colorCircles = colorCapsule.querySelectorAll('.color-circle');
    colorCircles.forEach(function (circle) {
        circle.classList.remove('selected');
    });

    // Marcar el color seleccionado
    colorCircle.classList.add('selected');

    // Actualizar el stock y habilitar el selector de cantidad
    var productoId = colorCapsule.id.split('-')[2];  // Obtener el ID del producto
    var cantidadSelector = document.getElementById('cantidad-selector-' + productoId);
    cantidadSelector.innerHTML = '';
    var stock = parseInt(colorCircle.dataset.stock);
    for (var i = 1; i <= stock; i++) {
        var opcion = document.createElement('option');
        opcion.value = i;
        opcion.text = i;
        cantidadSelector.appendChild(opcion);
    }
    cantidadSelector.disabled = false;

    // Actualizar el color de fondo
    var colorSelector = document.getElementById('color-selector-' + productoId);
    colorSelector.style.backgroundColor = colorCircle.style.backgroundColor;
}

$(document).on("click", ".eliminar-producto-en-pagar", function(event) {
    event.preventDefault(); // Evitar la acción predeterminada del enlace

    var button = $(this);
    var productId = button.data("producto-id");
    

    // Obtiene el arreglo actual de IDs de productos de localStorage
    var storedProducts = JSON.parse(localStorage.getItem("storedProducts")) || [];

    // Filtra el arreglo para excluir el producto que se va a eliminar
    storedProducts = storedProducts.filter(function(id) {
        return id !== productId;
    });

    // Actualiza el localStorage con el nuevo arreglo de productos
    localStorage.setItem("storedProducts", JSON.stringify(storedProducts));
    //localStorage.setItem("storedProductsColor", JSON.stringify(storedProductsColor));

    // Construir la URL con los datos y redirigir
    var url = '/carrito?storedProducts=' + encodeURIComponent(JSON.stringify(storedProducts));
    
    // Redirigir a la nueva URL
    window.location.href = url;

    showNotification("Producto eliminado del carrito.");
});

$(document).ready(function () {
    // Manejar el cambio en el selector de cantidad
    $('.cantidad-selector').on('change', function () {
        actualizarTotal();
    });

    function actualizarTotal() {
        var totalProductos = 0;
        var cantidadProductos = 0;

        // Recorrer todos los selectores de cantidad
        $('.cantidad-selector').each(function () {
            var cantidad = parseInt($(this).val());
            
            cantidadProductos = cantidadProductos + cantidad;

            var precioUnitario = parseFloat($(this).data('precio')); // Asegúrate de tener un atributo data-precio en tu selector
            

            if (!isNaN(cantidad) && !isNaN(precioUnitario)) {
                totalProductos += cantidad * precioUnitario;
            }
        });

        // Actualizar el contenido del elemento con el nuevo total
        $('.total-valor').text('$ ' + totalProductos.toFixed(2));
        $('.total-productos').text(cantidadProductos);
    }
});


//////////////////////////////////////////////////// para el select de color, por sea caso
/*document.addEventListener('DOMContentLoaded', function () {
    // Agregar eventos de cambio a todos los selectores de color
    var colorSelectores = document.querySelectorAll('.color-selector');
    colorSelectores.forEach(function (colorSelector) {
        colorSelector.addEventListener('change', function () {
            actualizarStockYCantidad(colorSelector);
            actualizarColorFondo(colorSelector);
        });
    });

    // Llamada inicial para establecer el stock y la cantidad predeterminados
    colorSelectores.forEach(function (colorSelector) {
        actualizarStockYCantidad(colorSelector);
        actualizarColorFondo(colorSelector);
    });

    
});

function actualizarStockYCantidad(colorSelector) {
    var productoId = colorSelector.dataset.productoId;
    var cantidadSelector = document.getElementById('cantidad-selector-' + productoId);
    var stock = parseInt(colorSelector.options[colorSelector.selectedIndex].dataset.stock);

    // Actualizar el stock y habilitar el selector de cantidad
    cantidadSelector.innerHTML = '';
    for (var i = 1; i <= stock; i++) {
        var opcion = document.createElement('option');
        opcion.value = i;
        opcion.text = i;
        cantidadSelector.appendChild(opcion);
    }
    cantidadSelector.disabled = false;
}

function actualizarColorFondo(colorSelector) {
    var productoId = colorSelector.dataset.productoId;
    var colorSeleccionado = colorSelector.options[colorSelector.selectedIndex].value;
    colorSelector.style.backgroundColor = colorSeleccionado;
    //colorSelector.style.color = colorSeleccionado;
}*/