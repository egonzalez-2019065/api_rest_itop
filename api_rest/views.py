from django.contrib.auth.models import User
from .models import Computer
from rest_framework import permissions, viewsets
from rest_framework.response import Response



from api_rest.serealizer import UserSerializer, ComputerSerializer


class UserViewSet(viewsets.ModelViewSet):
    # Endpoint que devuelve los usuarios
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

class ComputerViewSet(viewsets.ModelViewSet):
    # Enpoint para que devuelve las computadoras
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer

    # Definir los campos que no deben ser actualizados en un futuro
    protected_fields = ['purchase_date'] # Ejemplo

    def create(self, request, *args, **kwargs):
        # Obtener los datos del request
        serial_number = request.data.get('serial_number')
        
        try:
            # Verificar si la computadora ya existe por el número de serie
            computer = Computer.objects.get(serial_number=serial_number)

            # Comparar y filtrar los campos que no deben ser actualizados
            data = request.data.copy()  # Se hace una copia para no afectar a la data extraída
            for field in self.protected_fields:
                if field in data:
                    data.pop(field)  # Eliminar los campos protegidos de los datos enviados

            # Actualizar los campos permitidos
            serializer = self.get_serializer(computer, data=data, partial=True) # Creando la instancia de serializer para poder actualizar los datos
            serializer.is_valid(raise_exception=True) # Válida que los datos cumplan con los definido en el modelo, por ejemplo la longitud máxima y demás
            self.perform_update(serializer) # Actualiza en la base de datos
            return Response("Actualizado correctamente", serializer.data)
        
        except Computer.DoesNotExist:
            # Si la computadora no existe, creamos una nueva
            return super().create(request, *args, **kwargs)
