# Imagen base oficial de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libjpeg62-turbo \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    xfonts-base \
    && apt-get clean

# Crear directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el contenido del proyecto al contenedor
COPY . /app

# Instalar las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer el puerto en el contenedor
EXPOSE 8000

# Comando para levantar el servidor usando Gunicorn
CMD ["gunicorn", "CarritoCompras.wsgi:application", "--bind", "0.0.0.0:8000"]
