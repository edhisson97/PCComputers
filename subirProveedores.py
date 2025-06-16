import os
import django
import pandas as pd

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CarritoCompras.settings")
django.setup()

from operacion.models import Proveedor  # Reemplaza 'app' con el nombre de tu app

# Cargar archivo Excel
df = pd.read_excel("PROVEEDORES.xlsx", dtype={
    'ruc': str,
    'telefono': str
})

creados = 0
omitidos = 0

for _, row in df.iterrows():
    ruc = str(row['ruc']).strip().zfill(13)
    
    if not ruc.isdigit() or len(ruc) != 13:
        continue  # Ignorar ruc inválido

    # Verificar si ya existe
    if Proveedor.objects.filter(ruc=ruc).exists():
        omitidos += 1
        continue

    proveedor = Proveedor.objects.create(
        ruc=ruc,
        nombre=row['nombre'],
        ciudad=row.get('ciudad', ''),
        direccion=row.get('direccion', ''),
        contacto=row.get('contacto', ''),
        email=row.get('email', ''),
        telefono=str(row.get('telefono', '')).strip()
    )
    creados += 1

print(f"Proveedores creados: {creados}")
print(f"Proveedores omitidos (por RUC duplicado): {omitidos}")
