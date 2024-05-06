document.addEventListener("DOMContentLoaded", function () {
    var index = 0;
    var imagenes = document.querySelectorAll('.img-mantenimiento img');

    function mostrarSiguienteImagen() {
        imagenes[index].style.display = 'none';
        index = (index + 1) % imagenes.length;
        imagenes[index].style.display = 'block';
    }

    setInterval(mostrarSiguienteImagen, 4000); // Cambia la imagen cada 3000 milisegundos (3 segundos)

    //para desarrollo
    var indexDesarrollo = 0;
    var imagenesDesarrollo = document.querySelectorAll('.img-desarrollo img');
    function mostrarSiguienteImagenDesarrollo() {
        imagenesDesarrollo[indexDesarrollo].style.display = 'none';
        indexDesarrollo = (indexDesarrollo + 1) % imagenesDesarrollo.length;
        imagenesDesarrollo[indexDesarrollo].style.display = 'block';
    }

    setInterval(mostrarSiguienteImagenDesarrollo, 4000); // Cambia la imagen cada 3000 milisegundos (3 segundos)

    //para analisis
    var indexAnalisis = 0;
    var imagenesAnalisis = document.querySelectorAll('.img-analisis img');
    function mostrarSiguienteImagenAnalisis() {
        imagenesAnalisis[indexAnalisis].style.display = 'none';
        indexAnalisis = (indexAnalisis + 1) % imagenesAnalisis.length;
        imagenesAnalisis[indexAnalisis].style.display = 'block';
    }

    setInterval(mostrarSiguienteImagenAnalisis, 4000); // Cambia la imagen cada 3000 milisegundos (3 segundos)

    //para capacitaciones
    var indexCapacitaciones = 0;
    var imagenescapacitaciones = document.querySelectorAll('.img-capacitaciones img');
    function mostrarSiguienteImagenCapacitaciones() {
        imagenescapacitaciones[indexCapacitaciones].style.display = 'none';
        indexCapacitaciones = (indexCapacitaciones + 1) % imagenescapacitaciones.length;
        imagenescapacitaciones[indexCapacitaciones].style.display = 'block';
    }

    setInterval(mostrarSiguienteImagenCapacitaciones, 4000); // Cambia la imagen cada 3000 milisegundos (3 segundos)
});

/*******************MANTENIMIENTO */
function openModal(serviceId) {
    document.getElementById('modal-' + serviceId).style.display = 'block';
    
}

function closeModal(serviceId) {
    document.getElementById('modal-' + serviceId).style.display = 'none';
}

// Event listener para cerrar el modal cuando se hace clic fuera de él para cada modal
var modals = document.querySelectorAll('.modal');
modals.forEach(function(modal) {
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            var serviceId = modal.id.split('-')[1]; // Obtiene el ID del servicio
            closeModal(serviceId); // Cierra el modal
        }
    });
});

