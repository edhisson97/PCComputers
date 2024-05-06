var fondo = document.getElementById('fondo');
var desplegable = document.getElementById('desple');
var productos = document.getElementById('productos');

document.getElementById('item').addEventListener('mouseenter', function () {
    fondo.style.display = 'flex';
    desplegable.style.display = 'flex';
});

document.getElementById('item').addEventListener('mouseleave', function () {
    fondo.style.display = 'none';
    desplegable.style.display = 'none';
});

