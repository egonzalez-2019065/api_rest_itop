from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
from api_rest import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'computers', views.ComputerViewSet)
router.register(r'generated-tokens', views.TokenGeneratedViewSet)
router.register(r'historial-computer', views.HistorialComputerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token/', views.CostumTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api_peticion/', views.ItopPeticionView.as_view(), name='api_peticion'),
]
