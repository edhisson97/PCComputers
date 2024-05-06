
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


function mostrarModal(modal) {

    document.getElementById('modalFondo').style.display = 'block';
    modal.style.display = 'block';

    // Agregar un event listener al fondo oscuro para cerrar el modal al hacer clic en él
    document.getElementById('modalFondo').addEventListener("click", cerrarModal);
    updateCartButtons();
}

// Obtén todos los botones "Ver Detalles"
var botonesVerDetalles = document.querySelectorAll(".ver-detalles");

// Agrega un evento de clic a cada botón "Ver Detalles"
botonesVerDetalles.forEach(function (boton) {
    boton.addEventListener("click", function () {
        var modal = this.closest(".producto").querySelector(".modal");
        mostrarModal(modal);

        // Obtén la información del producto actual
        var producto = this.closest(".producto");
        var nombre = producto.querySelector("h3").textContent;
        var detalle = producto.querySelector(".detalle").textContent;
        var precio = producto.querySelector(".precio").textContent;
        // ... obtén la información adicional que necesites

        // Actualiza el contenido del modal con la información del producto actual
        modal.querySelector("h3").textContent = nombre;
        modal.querySelector(".detalle").textContent = detalle;
        modal.querySelector(".precio").textContent = precio;
        // ... actualiza el contenido con la información adicional
        
    });

});
// Función para cerrar el modal
function cerrarModal() {
    updateCartButtons();

    document.getElementById('modalFondo').style.display = 'none';
    
    // Obtén todos los modales y ciérralos
    var modales = document.querySelectorAll(".modal");
    modales.forEach(function (modal) {
        modal.style.display = 'none';
    });

    // Remover el event listener para evitar múltiples llamadas
    document.getElementById('modalFondo').removeEventListener("click", cerrarModal);
}

// Agrega un evento de clic al fondo oscuro para cerrar el modal
document.getElementById('modalFondo').addEventListener("click", cerrarModal);

// Obtén todos los elementos "Cerrar Modal"
var elementosCerrarModal = document.querySelectorAll(".cerrar-modal");

// Agrega un evento de clic a cada elemento "Cerrar Modal"
elementosCerrarModal.forEach(function (elemento) {
    elemento.addEventListener("click", function () {
        var modal = this.closest(".modal");
        cerrarModal(modal);
    });
    updateCartButtons();
});


//********imagenes productos**********************/
function cambiarImagen(urlImagen,modal) {
    modal.querySelector('.main_img').src = urlImagen;
}

/*****************color ******** */


