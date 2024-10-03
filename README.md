
# API Test

Este proyecto es una prueba del funcionamiento local antes de llevarlo a producción, el funcionamiento de este proyecto consiste en ser el middleware entre el cliente y el servicio de Itop.

## Requerimientos

El proyecto está basado en python puro para el ejecutable y para el API python utilizando el framework de Django para la estructura del proyecto y Django rest framework para las solicitudes web, nos enfocaremos en la instalación y el despliegue del API.

### Librerías
El usuario debería tener instalado en su entorno local.
 - python 3.12
Al instarlo debe tener en cuenta instarlo con pip (versión 24.2) para poder realizar la instalación de los paquetes que se encuentran en los requerimientos del proyecto.

## Despliegue

Para poder implementar y desplegar el proyecto, debemos tener en cuenta que se necesitarán estas variables de entorno: 
- DJANGO_SECRET_KEY=
- DB_NAME=
- DB_USER=
- DB_PASSWORD=
- DB_HOST=
- DB_PORT=
- SERVICE_URL=
- USER_SERVICE=
- PASSWORD_SERVICE=
- SECRET_KEY=
Ahora bien, teniendo instalado python, te localizas en el directorio en donde se encuentre el api, luego como primer paso se deben instalar las dependencias con el comando:

```bash
  pip install -r requirements.txt
```
Luego de haber creado las dependencias debemos migrar a la base de datos, se debe tener en cuenta que en principio se debe crear la base de datos en Mysql para poder migrar las tablas que Django utiliza, así como otras tablas creadas para el manejo de los datos, esto se hace utilizando el comando: 
```bash
    python manage.py migrate
```
Si llegase a fallar el comando, podría ser porque aún no se han creado o detectado las migraciones, las migraciones se crean así: 
```bash
    python manage.py makemigrations
```
Creadas las migraciones ya se podría migrar a la base de datos.
Una vez migradas las tablas se procede a crear el super usuario por defecto:
```bash
    python manage.py createsuperuser
```
Una vez creado, por seguridad se creará un nuevo usuario en la base de datos, esto lo haremos con la ayuda de la shell de python, que se inicializa así: 
```bash
    python manage.py shell
```
Una vez levantada la shell pega este código:
```bash
from django.contrib.auth.models import User
user = User.objects.create_user('user_example', '', 'contraseña')
user.save()
```
No dará algún mensaje en la base de datos, pero se puede verificar en la tabla **auth_user** en la BD. 
Ahora bien, se le deben agregar un solo permiso para que pueda solo realizar la petición necesaria (esto como implementación de seguridad) con la shell aún activa pega este código: 
```bash
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='user_example')

permission_to_user = Permission.objects.get(codename='add_pcomputer')
user.user_permissions.add(permission_to_user)
user.save()
```
De igual forma este comando no devuelve algún mensaje pero se puede comprobar en la tabla **auth_user_user_permissions**.

Una vez creado el usuario y otorgado el permiso necesario, se debe crear un token, esto para que pueda autenticarse el servicio en nuestra api, copia este código, aún con la shell activa: 

```bash
from api_rest.views import Prueba
Prueba.generate_and_print_token('user_example')
```
Esto devolverá el token, el cual debes copiar, pues lo utilizarás para poder crear el ejecutable para el cliente, aquí puedes ver el repo: 


 - [Recolección de datos automatizado](https://github.com/egonzalez-2019065/automatizacion_inventario)



Por útlimo, se debe procesder a levantar los servicios. 
#### Servicio web
```bash
    python manage.py runserver
```
### Servicio de qlcuster el cual ejecutará las tareas en segundo plano
```bash
  python manage.py qcluster
```

### Tarea programada para realizar la petición de ingreso de equipos al servicio 
```bash
  python manage.py create_schedule
```

