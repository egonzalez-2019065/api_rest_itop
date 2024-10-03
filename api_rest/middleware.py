from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from .models import AuthBlocked

class CheckBlacklistedAccessTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization') # Extrae el token de la petición
        if auth_header and auth_header.startswith('Bearer '): # Verifica que el token venga en el formato correcto
            token = auth_header.split(' ')[1] # Guarda únicamente el token
            try:
                AccessToken(token)  # Valida el token
                if AuthBlocked.objects.filter(token=token).exists():
                    raise PermissionDenied("El token está en la lista negra")
            except Exception as e:
                raise PermissionDenied("Token inválido")