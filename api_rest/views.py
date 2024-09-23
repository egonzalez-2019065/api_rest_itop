# Importaciones del framework
import re
from django.contrib.auth.models import User
from .models import BlacklistedAccessToken, Computer, SerialAndIDItop, TokenGenerated, HistorialComputer, APITok
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from dotenv import load_dotenv
import os
import base64
import requests
from requests.exceptions import RequestException
from rest_framework.views import APIView
import json
from urllib.parse import urlencode
import secrets


# Serializadores
from api_rest.serealizer import UserSerializer, ComputerSerializer, HistorialComputerSerializer, TokenGeneratedSerializer

# Configuración de las variables de entorno 
load_dotenv()

class UserViewSet(viewsets.ModelViewSet):
    # Endpoint que devuelve los usuarios
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']


class ComputerViewSet(APIView):
    # Solo permitir el método POST
    http_method_names = ['post']
    
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Campos que no deberían actualizarse, de momento ejemplos
    protected_fields = []
    
    def post(self, request, *args, **kwargs):
        # Procesar la data primero
        data = request.data
        print(data)
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extraer solo el token sin 'Bearer '
        print(token)
        if not token:
            return Response({"error": "Token no proporcionado"}, 400)

        try:
            # Obtener el número de serie
            serial_number = data.get('serialnumber')
            if not serial_number:
                return Response({"error": "Número de serie no proporcionado"}, 400)

            # Intentar obtener la computadora existente
            try:
                computer = Computer.objects.get(serialnumber=serial_number)
                return self.update_computer(computer, data, token)
            except Computer.DoesNotExist:
                return self.create_computer(data, token)

        except Exception as e:
            self._blacklist_token(token)
            return Response({"error": "No se pudo procesar al máquina"}, 400)

    def update_computer(self, computer, data, token):
        # Filtrar campos protegidos
        for field in self.protected_fields:
            data.pop(field, None)

        serializer = ComputerSerializer(computer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            self._blacklist_token(token)
            return Response({"message": "Actualizado correctamente"}, 200)

    def create_computer(self, data, token):
        serializer = ComputerSerializer(data=data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            self._blacklist_token(token)
            return Response({"message": "Equipo creado exitosamente", "data": serializer.data}, 201)

    def _blacklist_token(self, token):
        try:
            AccessToken(token)
            BlacklistedAccessToken.objects.create(token=token)
        except Exception as e:
            return Response({"message": "Error al mandar el token a la lista negra"}, 400)
        
class CostumTokenObtainPairView(APIView):
    '''
    # Función para guardar el token en la base de datos
    def post(self, request, *args, **kwargs):
        # Captura la respuesta para obtener el token
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']

        # Guarda el token en la base de datos
        TokenGenerated.objects.create(token = access_token)

        # Retornar solo el token de acceso
        return Response({'access': access_token})
    '''
    def post(self, request): 
        token = request.headers.get('token')
        try:
            api_key = APITok.objects.get(key=token)
        except APITok.DoesNotExist:
            return Response({"Token no válido"}, 401)
        except Exception as e:
            return Response({"Error al intentar generar el token"}, 500) 
        

        access = AccessToken.for_user(api_key.user)

        TokenGenerated.objects.create(token = access)
        return Response({
            'access': f"{access}",
        })

class ItopPeticionView(APIView):
    def post(self, request):
        # Obtener todas las computadoras
        computers = Computer.objects.all()

        # Arreglos para manejar las diferentes respuestas
        success_messages = []
        error_messages = []

        if not computers.exists():
            return Response({"message": "No hay computadoras para procesar."}, status=400)

        for computer in computers:
            # Preparando los datos extraídos
            fields = {
                    "name": computer.name,
                    "description": computer.description,
                    "org_id": computer.organization_id or 15,
                    "move2production": computer.move2production.strftime("%Y-%m-%d") if computer.move2production else None,
                    "serialnumber": computer.serialnumber,
                    "location_id": computer.location_id or 8,
                    "status": computer.status,
                    "brand_id": computer.brand_id or 104,
                    "model_id": computer.model_id or 105,
                    "purchase_date": computer.purchase_date.strftime("%Y-%m-%d") if computer.purchase_date else None,
                    "end_of_warranty": computer.end_of_warranty.strftime("%Y-%m-%d") if computer.end_of_warranty else None,
                    "osfamily_id": computer.osfamily_id or 106,
                    "osversion_id": computer.os_version_id or 107,
                    "cpu": computer.cpu,
                    "ram": computer.ram,
                    "type": computer.type
                }
            # Decidiendo si actualizará o agregará la computadora
            id_serialnumber = SerialAndIDItop.objects.filter(serial_number=computer.serialnumber)
            data = None
            if id_serialnumber:
                data = {
                    "operation": "core/update",
                    "class": "PC",
                    "comment": "Computadora actualizada desde el API",
                    "key": f"SELECT PC WHERE serialnumber = '{computer.serialnumber}'"
                }
            else: 
                data = {
                    "operation": "core/create",
                    "class": "PC",
                    "comment": "Computadora agregada desde el API",  
                    "output_fields": "name"
                }
            
            data["fields"] = fields
            print(data)
        
            # Convertirlo a JSON
            json_data = json.dumps(data)

            # Preparando la URl   
            encoded_json_data = urlencode({'json_data': json_data})
            # Preparación de las credenciales para agregarlas a los headers
            itop_url = os.getenv('ITOP_URL')
            username = os.getenv('USER_ITOP')
            password = os.getenv('PASSWORD_ITOP')

            # Codificación de las credenciales
            credentials = f'{username}:{password}'
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Preparación de los headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }
            # Enviar la url completa 
            url_base = f"{itop_url}&{encoded_json_data}"
            
            # Enviar la petición a iTop
            try:
                response = requests.request("POST", url_base, headers=headers)
                print(f'Respuesta Itop: {response.text}')
                # Convierte la respuesta a un json
                itop_response = response.json()
                # Validación de la respuesta general de Itop
                if response.status_code == 200:
                    # Guardar la computadora con el ID que devuelva Itop
                    # Convetir el diccionario a cadena de texto
                    itop_response_str = str(itop_response)
                    # Buscarlo en la cadena de texto
                    itop_id_match = re.search(r'PC::(\d+)', itop_response_str)
                    # ID extraído
                    itop_id_final = itop_id_match.group(1)
                    # Guarda el id de la respuesta de Itop y el número de serie
                    serial_number_instance, created = SerialAndIDItop.objects.get_or_create(
                        serial_number=computer.serialnumber,  # Buscar por el número de serie
                        defaults = {
                            'id_itop': itop_id_final  # Si no existe, crear con este id_itop
                        }
                    )

                    # Validación más detallada según el error que devuelva Itop
                    if itop_response['code'] == 0: 
                        # Procesar respuesta exitosa
                        historial_computer, created = HistorialComputer.objects.get_or_create(
                            serialnumber=computer.serialnumber,
                            defaults={
                                'name': computer.name,
                                'organization_id': computer.organization_id,
                                'location_id': computer.location_id,
                                'brand_id': computer.brand_id,
                                'model_id': computer.model_id,
                                'osfamily_id': computer.osfamily_id,
                                'type': computer.type,
                                'cpu': computer.cpu,
                                'os_version_id': computer.os_version_id,
                                'status': computer.status,
                                'ram': computer.ram,
                                'description': computer.description,
                                'move2production': computer.move2production,
                                'purchase_date': computer.purchase_date,
                                'end_of_warranty': computer.end_of_warranty,
                            })
                        if not created:
                            historial_computer.name = computer.name
                            historial_computer.organization_id = computer.organization_id
                            historial_computer.location_id = computer.location_id
                            historial_computer.brand_id = computer.brand_id
                            historial_computer.model_id = computer.model_id
                            historial_computer.osfamily_id = computer.osfamily_id
                            historial_computer.type = computer.type
                            historial_computer.cpu = computer.cpu
                            historial_computer.os_version_id = computer.os_version_id
                            historial_computer.status = computer.status
                            historial_computer.ram = computer.ram
                            historial_computer.description = computer.description
                            historial_computer.move2production = computer.move2production
                            historial_computer.purchase_date = computer.purchase_date
                            historial_computer.end_of_warranty = computer.end_of_warranty
                            historial_computer.save()

                        # Eliminar la computadora procesada
                        computer.delete()
                        
                        success_messages.append(f"Computadora {computer.serialnumber} fue agregada correctamente")
                    else:
                        error_messages.append(f"Error al procesar {computer.serialnumber}, {itop_response['message']} código: {itop_response['code']}")
                else: 
                    error_messages.append(f"Error al procesar {computer.serialnumber}, {response.text} código: {response.status_code}")
            except RequestException as req_err:
                error_messages.append(f"Error al realizar la petición para {computer.serialnumber}: {req_err}")
            except Exception as e:
                error_messages.append(f"Error fatal para {computer.serialnumber}: {e}")   

        # Respuesta final
        response_data = {
            "success_messages": success_messages,
            "error_messages": error_messages
        }

        return Response(response_data, status=200 if not error_messages else 400)     

# Vistas de comprobación
class TokenGeneratedViewSet(viewsets.ModelViewSet):
    queryset = TokenGenerated.objects.all()
    serializer_class = TokenGeneratedSerializer

class HistorialComputerViewSet(viewsets.ModelViewSet):
    queryset = HistorialComputer.objects.all()
    serializer_class = HistorialComputerSerializer




        
