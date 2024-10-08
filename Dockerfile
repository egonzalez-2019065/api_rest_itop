# Usa una imagen base oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias para MySQL 
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto a la imagen
COPY . .

# Recoger archivos estáticos
RUN python manage.py collectstatic --noinput

# Expone el puerto que usará Django
EXPOSE 8000
