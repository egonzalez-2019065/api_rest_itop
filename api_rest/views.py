# Importaciones del framework
from django.contrib.auth.models import User
from .models import Computer, TokenGenerated, HistorialComputer
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedAccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from dotenv import load_dotenv
import os
import base64
import requests

# Modelos
from api_rest.serealizer import UserSerializer, ComputerSerializer

# Configuración de las variables de entorno 
load_dotenv()

class UserViewSet(viewsets.ModelViewSet):
    # Endpoint que devuelve los usuarios
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

class ComputerViewSet(viewsets.ModelViewSet):
    # Endpoint que devuelve las computadoras
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Campos que no deberían actualizarse, de momento ejemplos
    protected_fields = ['move2production1', 'purchase_date']

    def create(self, request, *args, **kwargs):
        # Extraer el token desde los headers
        auth_header = request.headers.get('Authorization')

        # Verificar que el token está presente
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extraer solo el token sin 'Bearer '

            try:
                # Obtener los datos del request
                serial_number = request.data.get('serialnumber')
                
                # Verificar si la computadora ya existe por el número de serie
                computer = Computer.objects.get(serialnumber=serial_number)
                 # Comparar y filtrar los campos que no deben ser actualizados
                data = request.data.copy()  # Se hace una copia para no afectar a la data extraída
                for field in self.protected_fields:
                    if field in data:
                        data.pop(field)  # Eliminar los campos protegidos de los datos enviados

                # Actualizar los campos permitidos
                serializer = self.get_serializer(computer, data=data, partial=True) # Creando la instancia de serializer para poder actualizar los datos
                serializer.is_valid(raise_exception=True) # Válida que los datos cumplan con los definido en el modelo, por ejemplo la longitud máxima y demás
                self.perform_update(serializer) # Actualiza en la base de datos
                
                # Invalidar el token para que siempre sea único
                self._blacklist_token(token)
                return Response({"message": "Actualizado correctamente", "data": serializer.data})
                
            except Computer.DoesNotExist:
                # Si la computadora no existe, creamos una nueva
                response = super().create(request, *args, **kwargs)
                self._blacklist_token(token)
                return response
            except Exception as e:
                return Response({"Sucedió un error inesperado": str(e)}, status=400)
        
        else:
            return Response({"error": "Token no proporcionado"}, status=400)

    def _blacklist_token(self, token):
        try:
            # Validar el token
            AccessToken(token)

            # Añadir el token a la blacklist
            BlacklistedAccessToken.objects.create(token=token)

            return Response({"status": "Token añadido a la lista negra"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
class CostumTokenObtainPairView(TokenObtainPairView):
    # Función para guardar el token en la base de datos
    def post(self, request, *args, **kwargs):
        # Captura la respuesta para obtener el token
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']

        # Guarda el token en la base de datos
        TokenGenerated.objects.create(token = access_token)

        # Retornar solo el token de acceso
        return Response({'access': access_token})
    

class ItopPeticion:
    def itop_peticion():
        # Obtener ambas tablas para realizar la comparación
        computer = Computer.objects.all()
        HistorialComputer.objects.first()

        # Preparando los datos extraídos
        payload = {
            "hostname": computer.hostname,
            "organization": computer.organization,
            "location": computer.location,
            "marca": computer.marca,
            "modelo": computer.modelo,
            "os_system": computer.os_system,
            "type": computer.type,
            "processor": computer.processor,
            "os_version": computer.os_version,
            "serial_number": computer.serial_number,
            "status": computer.status,
            "ram": computer.ram,
            "disk_capacity": computer.disk_capacity,
            "disk_free": computer.disk_free,
            "start_date": computer.start_date.strftime("%Y-%m-%d"),
            "purchase_date": computer.purchase_date.strftime("%Y-%m-%d"),
            "end_date": computer.end_date.strftime("%Y-%m-%d")
        }

        # Preparación de las credenciales para agregarlas a los headers
        username  = os.getenv('USER_ITOP')
        passwrod = os.getenv('PASSWORD_ITOP')
        itop_urlt = os.getenv('ITOP_URL')

        # Codificación de las credenciales
        credentials = f'{username}:{passwrod}'
        encoded_credetials = base64.b64encode(credentials.encode()).decode()

        # Preparación de los headers para la petición
        headers = {
            'Authorization' : f'Basic {encoded_credetials}',
            'Content-type' : 'application/x-www-form-urlencoded'
        }

        # Preparación de la data para enviarla

        # Guardar la respuesta que traiga itop, en este caso el id, y el número de serie de la computadora que se guarde
        try: 
            response = requests.request("POST", )
            print('hola')
        except Exception as e: 
            print(f'Error para guardar los datos {e}')

        # Si itop responde de de forma exitosa hacer: 

            # Verificar que si no existe en la tabla de historial se agregue 

            # Agregadas todas las computadoras al historial limpiar la tabla 





        
