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

$(document).ready(function () {
    // Mostrar el modal al hacer clic en el campo de búsqueda
    $('#buscador').on('input', function () {
        $('#modalFondoBusqueda').fadeIn();
        $('#miModalBusqueda').fadeIn();
    });

    $('#buscar-btn').on('click', function () {
        $('#modalFondoBusqueda').fadeIn();
        $('#miModalBusqueda').fadeIn();
    });

    // Cerrar el modal al hacer clic en la "x" o fuera del modal
    $('.cerrar-modal, #modalFondoBusqueda').on('click', function () {
        $('#modalFondoBusqueda').fadeOut();
        $('#miModalBusqueda').fadeOut();
    });

    // Evento de entrada en el input de búsqueda
    $('#buscador').on('input', function () {
        // Ocultar el modal si el input de búsqueda está vacío
        if ($(this).val().trim() === '') {
            $('#modalFondoBusqueda').fadeOut();
            $('#miModalBusqueda').fadeOut();
        }
    });

    // Agrega un evento de clic a todos los elementos con la clase "articulo"
    $('.articulo').on('click', function () {
        // Aquí puedes realizar las acciones que desees al hacer clic en un artículo
        // Por ejemplo, obtener el texto del título del artículo
        var idArticulo = $(this).data('id');

        // Si quieres redirigir a una página específica, puedes usar window.location.href
        // Redirige a la página específica con el ID del artículo
        window.location.href = '/articulo?id=' + idArticulo;
    });
});

