from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
from api_rest import views

router = routers.DefaultRouter()
# Ruta deshabilitada para que no se puedan ver los usuarios creados
#router.register(r'zmnx3cv/users', views.UserViewSet)


urlpatterns = [
    # Rutas de adiministración prefijo "/mm3ajko"
    path('mm3ajko/D7PAj9ZHwHCUTPzKDqaENSWEZ1CnqV801tj0UFdXZG4a3eEg/', admin.site.urls),

    # Rutas de vistas agregadas para la administración desde Django
    path('', include(router.urls)),

    # Rutas desde los parametros 
    # Para validación con el prefijo /rKcuWDBUhiUYm2b368YFmgah
    path('rKcuWDBUhiUYm2b368YFmgah/tJt1SMV8Mp0Nt9YQLKqTp4X9NUCUmFPDd7kEW6B3TbD0c7ve/', views.CostumTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Para el ingreso de las computadoras /du0aVFRVq8uAX9d9R0kSMFr7
    path('du0aVFRVq8uAX9d9R0kSMFr7/65nkCGkE7VeUEnjzUdktz7AxqKfwddjGEQiYb9LwXZYxaKxw/', views.ComputerViewSet.as_view(), name='computer-create'),
]
