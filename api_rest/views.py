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
from requests.exceptions import RequestException
from rest_framework.views import APIView

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

    protected_fields = ['move2production', 'purchase_date']
    
    def post(self, request, *args, **kwargs):
        # Aquí va la lógica para crear o actualizar la computadora
        # Extraer el token desde los headers
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extraer solo el token sin 'Bearer '

            try:
                serial_number = request.data.get('serialnumber')
                computer = Computer.objects.get(serialnumber=serial_number)

                data = request.data.copy()
                for field in self.protected_fields:
                    if field in data:
                        data.pop(field)  # Eliminar campos protegidos

                # Actualizar los campos permitidos
                serializer = ComputerSerializer(computer, data=data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()

                self._blacklist_token(token)
                return Response({"message": "Actualizado correctamente", "data": serializer.data})

            except Computer.DoesNotExist:
                serializer = ComputerSerializer(data=request.data)
                if serializer.is_valid(): 
                    serializer.save()
                    self._blacklist_token(token)
                    return Response({"message": f"Equipo creado exitosamente {serializer.data}"})
                return Response(serializer.errors, status=400)

            except Exception as e:
                self._blacklist_token(token)
                return Response({"Sucedió un error inesperado": str(e)}, 400)

        else:
            return Response({"error": "Token no proporcionado"}, 400)

    def _blacklist_token(self, token):
        try:
            AccessToken(token)
            BlacklistedAccessToken.objects.create(token=token)
        except Exception as e:
            return Response({"error": str(e)}, 400)
        
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
    

class ItopPeticionView(APIView):
    def post(self, request):
        # Obtener ambas tablas para realizar la comparación
        computers = Computer.objects.all()

        if not computers.exists():
            return Response({"message": "No hay computadoras para procesar."}, status=400)

        for computer in computers:
            # Preparando los datos extraídos
            data = {
                "operation": "core/create",
                "class": "PC",
                "fields": {
                    "hostname": computer.name, 
                    "organization_name": computer.organization_name,
                    "location_name": computer.location_name,
                    "brand_name": computer.brand_name,
                    "model_name": computer.model_name,
                    "osfamily_name": computer.osfamily_name,
                    "type": computer.type,
                    "cpu": computer.cpu,
                    "os_version_name": computer.os_version_name,
                    "serialnumber": computer.serialnumber,
                    "status": computer.status,
                    "ram": computer.ram,
                    "description": computer.description,
                    "move2production": computer.move2production.strftime("%Y-%m-%d") if computer.move2production else None,
                    "purchase_date": computer.purchase_date.strftime("%Y-%m-%d") if computer.purchase_date else None,
                    "end_of_warranty": computer.end_of_warranty.strftime("%Y-%m-%d") if computer.end_of_warranty else None,
                }
            }

            # Preparación de las credenciales para agregarlas a los headers
            username = os.getenv('USER_ITOP')
            password = os.getenv('PASSWORD_ITOP')
            itop_url = os.getenv('ITOP_URL')

            # Codificación de las credenciales
            credentials = f'{username}:{password}'
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Preparación de los headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }

            # Enviar la petición a iTop
            try:
                response = requests.post(itop_url, json=data, headers=headers)
                print(response)
                if response.status_code == 200:
                    # Procesar respuesta exitosa
                    historial_computer, created = HistorialComputer.objects.get_or_create(
                        serialnumber=computer.serialnumber,
                        defaults={
                            'name': computer.name,
                            'organization_name': computer.organization_name,
                            'location_name': computer.location_name,
                            'brand_name': computer.brand_name,
                            'model_name': computer.model_name,
                            'osfamily_name': computer.osfamily_name,
                            'type': computer.type,
                            'cpu': computer.cpu,
                            'os_version_name': computer.os_version_name,
                            'status': computer.status,
                            'ram': computer.ram,
                            'description': computer.description,
                            'move2production': computer.move2production,
                            'purchase_date': computer.purchase_date,
                            'end_of_warranty': computer.end_of_warranty,
                        })
                    if not created:
                        historial_computer.name = computer.name
                        historial_computer.organization_name = computer.organization_name
                        historial_computer.location_name = computer.location_name
                        historial_computer.brand_name = computer.brand_name
                        historial_computer.model_name = computer.model_name
                        historial_computer.osfamily_name = computer.osfamily_name
                        historial_computer.type = computer.type
                        historial_computer.cpu = computer.cpu
                        historial_computer.os_version_name = computer.os_version_name
                        historial_computer.status = computer.status
                        historial_computer.ram = computer.ram
                        historial_computer.description = computer.description
                        historial_computer.move2production = computer.move2production
                        historial_computer.purchase_date = computer.purchase_date
                        historial_computer.end_of_warranty = computer.end_of_warranty
                        historial_computer.save()

                    # Eliminar la computadora procesada
                    computer.delete()
                
                    return Response({"message: Datos guardados excitosamente"}, 200)
                else:
                    '''
                        Else modificado para pasar el test, funciones temporales
                    '''
                    '''
                    # Procesar respuesta exitosa
                    historial_computer, created = HistorialComputer.objects.get_or_create(
                        serialnumber=computer.serialnumber,
                        defaults={
                            'name': computer.name,
                            'organization_name': computer.organization_name,
                            'location_name': computer.location_name,
                            'brand_name': computer.brand_name,
                            'model_name': computer.model_name,
                            'osfamily_name': computer.osfamily_name,
                            'type': computer.type,
                            'cpu': computer.cpu,
                            'os_version_name': computer.os_version_name,
                            'status': computer.status,
                            'ram': computer.ram,
                            'description': computer.description,
                            'move2production': computer.move2production,
                            'purchase_date': computer.purchase_date,
                            'end_of_warranty': computer.end_of_warranty,
                        })
                    if not created:
                        historial_computer.name = computer.name
                        historial_computer.organization_name = computer.organization_name
                        historial_computer.location_name = computer.location_name
                        historial_computer.brand_name = computer.brand_name
                        historial_computer.model_name = computer.model_name
                        historial_computer.osfamily_name = computer.osfamily_name
                        historial_computer.type = computer.type
                        historial_computer.cpu = computer.cpu
                        historial_computer.os_version_name = computer.os_version_name
                        historial_computer.status = computer.status
                        historial_computer.ram = computer.ram
                        historial_computer.description = computer.description
                        historial_computer.move2production = computer.move2production
                        historial_computer.purchase_date = computer.purchase_date
                        historial_computer.end_of_warranty = computer.end_of_warranty
                        historial_computer.save()

                    # Eliminar la computadora procesada
                    computer.delete()
                    return Response({"message": "Datos guardados exitosamente"}, 200)
                    '''
                    return Response({"message": f"Error al realizar la petición a Itop: {response.text}"}, 401)
            except RequestException as req_err:
                return Response({"message" : f"Error al realizar la petición, algo salió mal. {req_err}"}, response.status_code)
            except Exception as e: 
                return Response({"message": f"Error fatal, algo salió mal. {e}"}, 500)
            

# Vistas de comprobación
class TokenGeneratedViewSet(viewsets.ModelViewSet):
    queryset = TokenGenerated.objects.all()
    serializer_class = TokenGeneratedSerializer

class HistorialComputerViewSet(viewsets.ModelViewSet):
    queryset = HistorialComputer.objects.all()
    serializer_class = HistorialComputerSerializer




        
