import os
import django
import pandas as pd

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CarritoCompras.settings")  # Reemplaza 'tu_proyecto' con el nombre de tu proyecto
django.setup()

from django.contrib.auth.models import User
from inicio.models import adicionalUsuario  # Reemplaza 'app' con el nombre de tu app

# Cargar archivo Excel
df = pd.read_excel("CLIENTES.xlsx", dtype={'cedula': str, 'celular': str})  # Asegúrate de que el archivo esté en la misma carpeta que este script

for _, row in df.iterrows():
    email = str(row['email']).strip().lower()
    first_name = str(row['Nombres']).strip() if pd.notna(row['Nombres']) else ''
    last_name = str(row['Apellidos']).strip() if pd.notna(row['Apellidos']) else ''
    cedula = str(row['cedula']).strip()
    celular = str(row['celular']).strip() if pd.notna(row['celular']) else ''
    ciudad = str(row['ciudad']).strip()
    direccion = str(row['direccion']).strip()
    direccion_envio = str(row['direccionEnvio']).strip()

    if not email or not cedula:
        continue  # Saltar filas incompletas

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    adicionalUsuario.objects.get_or_create(
        user=user,
        cedula=cedula,
        defaults={
            'token': None,
            'celular': celular,
            'ciudad': ciudad,
            'direccion': direccion,
            'direccionEnvio': direccion_envio,
            'deuda': 'no'
        }
    )

print("Importación completada.")
