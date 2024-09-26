# Importaciones del framework
import re
from django.contrib.auth.models import User
from .models import BlacklistedAccessToken, Computer, TokenGenerated, APITok
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from django_q.tasks import async_task
from dotenv import load_dotenv

# Serializadores
from api_rest.serealizer import UserSerializer, ComputerSerializer

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

    # Endpoint que permite la creación de una nueva computadora
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Campos que no deberían actualizarse
    protected_fields = ['organization_id', 'location_id', 'brand_id', 'model_id', 'osfamily_id', 'os_version_id']
    
    def post(self, request, *args, **kwargs):
        # Procesar la data primero
        data = request.data
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extraer solo el token sin 'Bearer '
        if not token:
            return Response({"error": "Token no proporcionado"}, 400)

        try:
            # Obtener el número de serie
            serial_number = data.get('serialnumber')
            if not serial_number:
                return Response({"error": "Número de serie no proporcionado"}, 400)

            # Intentar obtener la computadora si es que existe
            try:
                computer = Computer.objects.get(serialnumber=serial_number)
                return self.update_computer(computer, data, token)
            except Computer.DoesNotExist:
                return self.create_computer(data, token)
        except Exception as e:
            #self._blacklist_token(token)
            return Response({"error": f"No se pudo procesar al máquina {e}"}, 400)
    
    # Actualizar una computadora existente
    def update_computer(self, computer, data, token):
        # Filtrar campos protegidos
        for field in self.protected_fields:
            data.pop(field, None)
        serializer = ComputerSerializer(computer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            self._blacklist_token(token)
            return Response({"message": "Equipo actualizado correctamente"}, 200)
        return Response(serializer.errors, status=400)  # Retornar errores de validación

    # Crear una nueva computadora
    def create_computer(self, data, token):
        serializer = ComputerSerializer(data=data, context={'request': self.request})
        if serializer.is_valid():
            async_task('api_rest.tasks.clear', data) # Iniciar la tarea asíncronica para limpiar la data
            #self._blacklist_token(token) 
            return Response({"message": "Equipo creado exitosamente"}, 201)
        return Response(serializer.errors, status=400)  # Retornar errores de validación

    # Mandar el token a la lista negra e inválidarlo luego de su consumo
    def _blacklist_token(self, token):
        try:
            AccessToken(token)
            BlacklistedAccessToken.objects.create(token=token)
        except Exception as e:
            return Response({"message": "Error al mandar el token a la lista negra"}, 400)
        
class CostumTokenObtainPairView(APIView):
    '''
    #
    #   Comentada debido al cambio en la forma en que se válida el token (Documentación)
    #
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

    # Función que obtiene el token y retorna un JWT 
    def post(self, request): 
        token = request.headers.get('token')
        try:
            api_key = APITok.objects.get(key=token)
        except APITok.DoesNotExist:
            return Response({"Token no válido"}, 401)
        except Exception as e:
            return Response({"Error al intentar generar el token"}, 500) 
        
        # Creación del JWT
        access = AccessToken.for_user(api_key.user)
        TokenGenerated.objects.create(token = access)
        return Response({
            'access': f"{access}",
        })


'''
#
#   Comentada debido ya que su uso es únicamente si se quisiera crear un token para un usuario, 
#       en vez de utilizar sus credenciales
#
# Función provisional para crear un token:
import secrets
class Prueba: 
    @staticmethod
    def generate_unique_token(user):
        # Genera un token único
        token = secrets.token_urlsafe(32)

        # Verifica si el token ya existe para evitar duplicados
        while APITok.objects.filter(key=token).exists():
            token = secrets.token_urlsafe(32)

        # Guarda el token en la base de datos
        APITok.objects.create(key=token, user=user)

        return token
    
    @staticmethod
    def generate_and_print_token(username):
        try:
            user = User.objects.get(username=username)
            token = Prueba.generate_unique_token(user)
            print("Token generado:", token)
        except User.DoesNotExist:
            print("Usuario no encontrado.")   

#
#   Comando para ejecutarla en la shell: 
#       from api_rest.views import Prueba  
#       Prueba.generate_and_print_token('user_example') -> Colocar un usuario existente en la DB	
#  
'''


        
