from django.db import connection
from django.apps import apps

# Diccionario: app_name -> lista de modelos de esa app
modelos_por_app = {
    'operacion': [
        'Caja',
    ],
    'ventas': [
        'Factura',
        'FacturaCredito',
        'Servicio',
        'PagoServicio',
        'PagoServicioCombinado',
    ],
}

for app_name, modelos in modelos_por_app.items():
    for model_name in modelos:
        model = apps.get_model(app_name, model_name)
        model.objects.all().delete()
        with connection.cursor() as cursor:
            table_name = model._meta.db_table
            if connection.vendor == 'sqlite':
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
            elif connection.vendor == 'postgresql':
                cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
            elif connection.vendor == 'mysql':
                cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
