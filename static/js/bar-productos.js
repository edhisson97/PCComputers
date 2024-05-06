/*******************para la navbar ****************** */
document.addEventListener("DOMContentLoaded", function() {
    const categories = document.querySelectorAll(".category");

    // Obtener el estado actual de selección desde el almacenamiento local
    const selectedCategoryId = localStorage.getItem('selectedCategoryId');

    categories.forEach(category => {
        category.addEventListener("click", () => {
            // Remover la clase 'selected' de todas las categorías
            categories.forEach(cat => cat.classList.remove("selected"));

            // Agregar la clase 'selected' a la categoría clicada
            category.classList.add("selected");

            // Obtener el ID de la subcategoría
            const subcategoriaId = category.getAttribute("data-subcategoria-id");
            const categoriaId = category.getAttribute("data-categoria-id");
            
            // Almacenar el estado actual de selección en el almacenamiento local
            localStorage.setItem('selectedCategoryId', subcategoriaId);
            
            // Redirigir a la página de productos con el ID de subcategoría en la URL
            if (subcategoriaId) {
                window.location.href = `/productos/${categoriaId}?subcategoria_id=${subcategoriaId}`;
            } else {
                // Para el caso de "TODO" o cualquier acción adicional
                window.location.href = `/productos/${categoriaId}`;
            }
        });


        // Restaurar la selección al cargar la página
        if (selectedCategoryId && category.getAttribute("data-subcategoria-id") === selectedCategoryId) {
            category.classList.add("selected");
        } else {
            category.classList.remove("selected");
        }


    });
    
});

/******************para clasificar por precio */
$(document).ready(function () {
    const dropdownContent = $("#precioDropdown .custom-dropdown-content");

    // Mostrar u ocultar las opciones al hacer clic en el botón
    $("#precioDropdown .custom-dropdown-btn").click(function () {
        dropdownContent.toggleClass("show");
    });

    // Manejar la selección de la opción
    dropdownContent.find("a").click(function (event) {
        event.preventDefault();

        const option = $(this);
        const selectedText = option.attr("data-option");

        // Actualizar el título del dropdown con la opción seleccionada
        $("#precioDropdown .custom-dropdown-btn").text(`Clasificar por precio (${selectedText})`);

        // Almacenar la opción seleccionada en el almacenamiento local
        localStorage.setItem('selectedOption', selectedText);

        // Obtener el valor de subcategoria almacenado en 'selectedCategoryId'
        var subcategoriaId = localStorage.getItem('selectedCategoryId');
        var marcaId = localStorage.getItem('selectedMarca');
        ///verifico si categoria es null

        // Redirigir a la vista de Django con la opción seleccionada y la categoría actual
        const categoriaActual = option.attr("data-categoria-id");
        const redirectUrl = `/productos/${categoriaActual}?opcion=${selectedText}&subcategoria_id=${subcategoriaId}&marca=${marcaId}`;
        console.log('Redirigiendo a:', redirectUrl);
        window.location.href = redirectUrl;
    });

    // Cerrar el menú desplegable al hacer clic fuera de él
    $(document).click(function (event) {
        if (!$(event.target).closest("#precioDropdown").length) {
            dropdownContent.removeClass("show");
        }
    });
});


/********************************para clasificar por marca */
$(document).ready(function () {
    const marcaDropdownContent = $("#marcaDropdown .custom-dropdown-content");

    // Mostrar u ocultar las opciones al hacer clic en el botón
    $("#marcaDropdown .custom-dropdown-btn").click(function () {
        marcaDropdownContent.toggleClass("show");
    });

    // Manejar la selección de la opción
    marcaDropdownContent.find("a").click(function (event) {
        event.preventDefault();

        const option = $(this);
        const selectedText = option.attr("data-option");

        // Actualizar el título del dropdown con la opción seleccionada
        $("#marcaDropdown .custom-dropdown-btn").text(`Seleccionar marca (${selectedText})`);

        // Almacenar la opción seleccionada en el almacenamiento local
        localStorage.setItem('selectedMarca', selectedText);

        // Obtener el valor de subcategoria almacenado en 'selectedCategoryId'
        var subcategoriaId = localStorage.getItem('selectedCategoryId');

        var selectedOption = localStorage.getItem('selectedOption');
        ///verifico si categoria es null

        // Redirigir a la vista de Django con la opción seleccionada y la categoría actual
        const categoriaActual = option.attr("data-categoria-id");
        const redirectUrl = `/productos/${categoriaActual}?marca=${selectedText}&subcategoria_id=${subcategoriaId}&opcion=${selectedOption}`;
        console.log('Redirigiendo a:', redirectUrl);
        window.location.href = redirectUrl;
    });

    // Cerrar el menú desplegable al hacer clic fuera de él
    $(document).click(function (event) {
        if (!$(event.target).closest("#marcaDropdown").length) {
            marcaDropdownContent.removeClass("show");
        }
    });
});
