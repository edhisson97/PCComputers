#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Crear superusuario automáticamente si no existe
#python manage.py shell <<EOF
#from django.contrib.auth import get_user_model
#User = get_user_model()
#username = "*****"
#email = "*******@gmail.com"
#password = "****"

#if not User.objects.filter(username=username).exists():
#    User.objects.create_superuser(username, email, password)
#    print("Superusuario creado con éxito.")
#else:
#    print("El superusuario ya existe.")
#EOF

#python subirClientes.py
#python subirProveedores.py