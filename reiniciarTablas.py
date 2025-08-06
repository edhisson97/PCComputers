from django.db import connection
from django.apps import apps

# Lista de tus modelos
models = [
    'Caja',
    'Factura',
    'FacturaCredito',
    'Servicio',
    'PagoServicio',
    'PagoServicioCombinado',
]

# Elimina todos los registros y reinicia el ID
for model_name in models:
    model = apps.get_model('CarritoCompras', model_name)  # Reemplaza con el nombre real de tu app
    model.objects.all().delete()
    with connection.cursor() as cursor:
        table_name = model._meta.db_table
        if connection.vendor == 'sqlite':
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
        elif connection.vendor == 'postgresql':
            cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
        elif connection.vendor == 'mysql':
            cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
