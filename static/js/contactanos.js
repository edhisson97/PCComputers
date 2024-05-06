function initMap() {
    // Puedes personalizar las coordenadas y opciones del mapa según tu ubicación
    var map = new google.maps.Map(document.getElementById('google-map'), {
        center: { lat: 0, lng: 0 }, // Coordenadas del centro del mapa
        zoom: 14, // Nivel de zoom
    });
    var marker = new google.maps.Marker({
        position: { lat: 0, lng: 0 }, // Coordenadas del marcador
        map: map,
        title: 'Matriz XYZ', // Título del marcador
    });
}
