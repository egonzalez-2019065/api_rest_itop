from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedAccessToken

class CheckBlacklistedAccessTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                AccessToken(token)  # Valida el token
                if BlacklistedAccessToken.objects.filter(token=token).exists():
                    raise PermissionDenied("Se agregó el token a la blacklist")
            except Exception as e:
                raise PermissionDenied("Token inválido")