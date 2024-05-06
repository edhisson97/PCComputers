function cambiarImagenArticulo(nuevaUrl) {
    // Cambia la URL de la imagen principal
    document.querySelector('.main_img').src = nuevaUrl;
}


$(document).ready(function () {
    $('.articulo-sugerido').on('click', function () {
        // Aquí puedes realizar las acciones que desees al hacer clic en un artículo
        // Por ejemplo, obtener el texto del título del artículo
        var idArticulo = $(this).data('id');

        // Obtiene la URL base actual
        var baseURL = window.location.origin;

        // Si quieres redirigir a una página específica, puedes usar window.location.href
        // Redirige a la página específica con el ID del artículo
        window.location.href =  baseURL + '/articulo?id=' + idArticulo;
        //window.location.href = '/'
    });



    $('#filtroGeneral').change(function () {
        var selectedOption = $(this).find(':selected').data('option');
        var selectedCategoriaId = $(this).find(':selected').data('categoria-id');
        console.log('Opción seleccionada:', selectedOption);
        console.log('Categoria ID:', selectedCategoriaId);

        // Verificar si selectedOption es un número o no
        if (!isNaN(selectedOption)) {
            console.log('selectedOption es un número.');
            // Aquí puedes realizar acciones específicas si selectedOption es un número
            var redirectUrl = `/productos/${selectedCategoriaId}?marca=${selectedOption}`;
        } else {
            // Construir la URL de redirección
            var redirectUrl = `/productos/${selectedCategoriaId}?opcion=${selectedOption}`;
        }

        //var redirectUrl = `/productos/${selectedCategoriaId}?opcion=${selectedOption}&subcategoria_id=${subcategoriaId}&marca=${marcaId}`;
        console.log('Redirigiendo a:', redirectUrl);

        // Redirigir a la URL
        window.location.href = redirectUrl;
    });
});

document.addEventListener("DOMContentLoaded", function() {
    var productosSugeridos = document.querySelectorAll('.articulo-sugerido');

    // Función para mostrar productos en un intervalo
    function mostrarProductos() {
        productosSugeridos.forEach(function(prod, index) {
            setTimeout(function() {
                prod.classList.add('mostrar');
            }, index * 500); // Ajusta el intervalo entre cada producto según sea necesario
        });
    }

    // Mostrar productos al cargar la página
    mostrarProductos();

    // Configura la función para que se ejecute cada cierto tiempo
    setInterval(function() {
        // Reinicia la animación ocultando los productos antes de mostrar nuevamente
        productosSugeridos.forEach(function(prod) {
            prod.classList.remove('mostrar');
        });

        // Muestra los productos después de ocultarlos
        setTimeout(mostrarProductos, 500);
    }, 10000); // Ajusta el intervalo según sea necesario
});


