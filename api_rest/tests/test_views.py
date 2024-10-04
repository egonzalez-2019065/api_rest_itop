from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api_rest.models import PComputer, AuthBlocked
from unittest.mock import patch


class ComputerViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Datos de prueba para la computadora
        self.data = {
            'serialnumber': 'PF33X004',
            'name': 'Test Computer',
            'organization_id': 'el salvador',
            'location_id': 1,
            'brand_id': 1,
            'model_id': 1,
            'osfamily_id': 1,
            'os_version_id': 1,
            'type': 'desktop',
            'cpu': 'Intel i7',
            'ram': 16,
            'status': 'active',
            'description': 'A test computer',
            'move2production': '2024-01-01',
            'purchase_date': '2024-01-01',
            'end_of_warranty': '2025-01-01'
        }
    

    # Función que verifica la creación de una nueva computadora
    def test_create_computer_success(self):
        # Crear la computadora
        response = self.client.post(reverse('computer'), data=self.data, format='json')

        # Validaciones
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Equipo creado exitosamente.')
        self.assertEqual(AuthBlocked.objects.count(), 1) 

    # Verificar que la computadora no se crea si no tiene el número de serie
    def test_create_computer_no_serialnumber(self):
        # Crear una copia para no editar la data original
        data_no_serial = self.data.copy()
        data_no_serial.pop('serialnumber')

        # Realizamos la petición
        response = self.client.post(reverse('computer'), data=data_no_serial, format='json')

        # Validaciones
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Número de serie no proporcionado.')
        self.assertEqual(AuthBlocked.objects.count(), 1)


    # Test para verificar que la computadora se actualiza al ya estar creada
    def test_update_computer_success(self):
        # Primero, creamos la computadora
        PComputer.objects.create(**self.data)
        
        # Ahora, intentamos actualizarla
        update_data = {
            'serialnumber': 'PF33X004',
            'name': 'Updated Computer'
        }

        # Realizamos las petición
        response = self.client.post(reverse('computer'), data=update_data, format='json')

        # Validaciones
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Equipo actualizado correctamente.')
        self.assertEqual(AuthBlocked.objects.count(), 1)


        # Verificar que los cambios se han aplicado
        computer = PComputer.objects.get(serialnumber='PF33X004')
        self.assertEqual(computer.name, 'Updated Computer')

