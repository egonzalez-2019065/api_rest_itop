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
**3.4. Aplique las migraciones:**

Es importante hacer mención que hay una configuración necesaria para desplegar el proyecto, y esto es cambiar el **"DEBUG"** de True a False y por consecuencia hacer los pasos necesarios para que interfaz de Django siga siendo visible. 


**4.3.4 Recrear los archivos estáticos para la interfaz gráfica de django:**

Al llevar esto a producción se deben hacer unos ajustes necesarios, en principio se deben configurar los hosts permitidos, por defecto están: 
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```
También se pudiera dejar el acceso libre, que no es lo recomendado, pero se harí así:

```python
ALLOWED_HOSTS = [*]
```

Esto no hace referencia a los clientes (equipos)  si no al servidor donde se hará el despliegue.

Para que la interfaz de Django no esté en texto plano, debe ejecutar este comando:

```bash
python manage.py collectstatic
```

Que este comando lo que hace es recopilar los archivos estáticos, estos los cuales permiten que la interfaz gráfica sea accesible y contenga el formato esperado, si estos no se llegasen a colectar, la interfaz se vería sin formato ni estilo, más que en texto plano. 

Y con esto se ya se podría ingresar a la administración de Django de forma gráfica.

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
from api_rest.views import GenerateToken
GenerateToken.generate_and_print_token('user_example')
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