# API Test

## Descripción del Proyecto

Este proyecto funciona como un middleware entre el cliente y el servicio de Itop. Está diseñado para ser probado localmente antes de su implementación en producción, asegurando así su correcto funcionamiento y robustez.

## Requisitos Técnicos

El proyecto se basa en Python puro para el ejecutable, mientras que la API utiliza el framework Django para la estructura del proyecto y Django Rest Framework para gestionar las solicitudes web. A continuación, se detallan los requisitos principales:

### Entorno de Desarrollo
- Python 3.12
- pip 24.2 (para la instalación de paquetes)

## Proceso de Implementación

### 1. Configuración del Entorno

Antes de comenzar, es necesario configurar las siguientes variables de entorno:

- DJANGO_SECRET_KEY
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- SERVICE_URL
- USER_SERVICE
- PASSWORD_SERVICE
- SECRET_KEY

### 2. Instalación de Dependencias

Posiciónese en el directorio del proyecto y ejecute:

```bash
pip install -r requirements.txt
```

### 3. Configuración de la Base de Datos

**3.1. Cree la base de datos en MySQL.**

**3.2. Genere las migraciones:**

-  Es importante que sepa que si no se encuentran migraciones simplemente basta con ejecutar el siguiente comando (migrate)

```bash
python manage.py makemigrations
```
**3.3. Aplique las migraciones:**
```bash
python manage.py migrate
```

### 4. Creación de Usuarios

**4.1. Cree un superusuario:** Este permitirá utilizar la interfaz gráfica de Django, ahí podrá crear más usuarios y otorgarle permisos, entre otros:
```bash
python manage.py createsuperuser
```

**4.2. Cree un usuario adicional:** Podrá usar la shell de Django, esto para implementar seguridad al proyecto, pues este usuario será el cual permita al ejecutable autenticarse, para ello inicie la shell:
```bash
python manage.py shell
```
En la shell, ejecute:
```python
from django.contrib.auth.models import User
user = User.objects.create_user('user_example', '', 'contraseña')
user.save()
```

**4.3. Asigne permisos al nuevo usuario:** Este permiso permitirá únicamente agregar computadoras:
```python
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='user_example')
permission_to_user = Permission.objects.get(codename='add_pcomputer')
user.user_permissions.add(permission_to_user)
user.save()
```

**4.4. Genere un token para el usuario:**
```python
from api_rest.views import Prueba
Prueba.generate_and_print_token('user_example')
```
guarde este token, con este token podrá validarse el ejecutable en la API.

### 5. Ejecución de Servicios

**5.1. Inicie el servidor web:**
```bash
python manage.py runserver
```

**5.2. Ejecute las tareas programadas:**
```bash
python manage.py create_schedule
```

## Notas Adicionales

Para la implementación del ejecutable del cliente, consulte el siguiente repositorio:
[Recolección de datos automatizado](https://github.com/egonzalez-2019065/automatizacion_inventario)

Una vez completados estos pasos, la API estará lista para recibir solicitudes del ejecutable en los equipos cliente y realizar peticiones al servicio para mantener actualizado el inventario.