# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt .

# Insala las dependencias para mysql 
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto a la imagen
COPY . .

# Expone el puerto que usará Django
EXPOSE 8000

# Comando para correr la aplicación
CMD ["gunicorn", "manage.py", "runserver", "0.0.0.0:8000"]
