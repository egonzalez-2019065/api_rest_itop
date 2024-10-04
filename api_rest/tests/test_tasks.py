from unittest.mock import MagicMock
from django.test import TestCase, Client
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken
from api_rest.tasks.task_clean_data import clear
from api_rest.models import Data, PComputer, HistorialPComputer, SerialAndService
from django.contrib.auth.models import User
from api_rest.tasks.task_insert_data import insert
import os


class ComputerTaskTest(TestCase):
 # Probar tarea asíncronica
    def setUp(self):
       Data.objects.create(
        serialnumber='PF33X004',
        name='Test Computer',
        organization_id='el salvador',
        location_id='el salvador',
        brand_id='Lenovo',
        model_id='Thinkpad',
        osfamily_id='Windows',
        os_version_id='Pro 10',
        type='desktop',
        cpu='Intel i7',
        ram=16,
        status='production',
        description='1000 GB y 20 disponibles',
        move2production='2024-01-01',
        purchase_date='2024-01-01',
        end_of_warranty='2025-01-01'
    )
    def test_task_clear(self):
        clear()
        self.assertIsNone(Data.objects.filter(serialnumber = 'PF33X004').first())
        self.assertIsNotNone(PComputer.objects.filter(serialnumber = 'PF33X004').first())
        self.assertEqual(PComputer.objects.get().serialnumber, 'PF33X004')
        self.assertEqual(PComputer.objects.get().name, 'Test Computer')

class ServiceInsertTest(TestCase):

    def setUp(self):
        # Credenciales para el token de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        # Generar un token de acceso usando SimpleJWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        # Computadoras de prueba 
        self.computers = [
            PComputer.objects.create(
                name='Computer 1',
                description='',
                organization_id=None,
                move2production=None,
                serialnumber='SN001',
                location_id=None,
                status='production',
                brand_id=None,
                model_id=None,
                purchase_date=None,
                end_of_warranty=None,
                osfamily_id=None,
                os_version_id=None,
                cpu='Intel i5',
                ram=8,
                type='desktop'
            ),
            PComputer.objects.create(
                name='Computer 2',
                description='',
                organization_id=None,
                move2production=None,
                serialnumber='SN002',
                location_id=None,
                status='production',
                brand_id=None,
                model_id=None,
                purchase_date=None,
                end_of_warranty=None,
                osfamily_id=None,
                os_version_id=None,
                cpu='AMD Ryzen 5',
                ram=16,
                type='laptop'
            ),
            PComputer.objects.create(
                name='Computer 3',
                description='',
                organization_id=None,
                move2production=None,
                serialnumber='SN003',
                location_id=None,
                status='production',
                brand_id=None,
                model_id=None,
                purchase_date=None,
                end_of_warranty=None,
                osfamily_id=None,
                os_version_id=None,
                cpu='Intel i9',
                ram=32,
                type='desktop'
            ),
            PComputer.objects.create(
                name='Computer 4',
                description='',
                organization_id=None,
                move2production=None,
                serialnumber='SN004',
                location_id=None,
                status='production',
                brand_id=None,
                model_id=None,
                purchase_date=None,
                end_of_warranty=None,
                osfamily_id=None,
                os_version_id=None,
                cpu='Intel i7',
                ram=16,
                type='desktop'
            )
        ]

        # Configurar variables de entorno mock
        os.environ['SERVICE_URL'] = 'https://mock-servicio-url.com'
        os.environ['USER_SERVICE'] = 'mockuser'
        os.environ['PASSWORD_SERVICE'] = 'mockpassword'

    # Test para ver si se crean las computadoras en el servicio
    @patch('api_rest.tasks.task_insert_data.requests.request')
    @patch('api_rest.tasks.task_insert_data.look')
    def test_insert_computer_success(self, mock_look, mock_request):

        id_counter = 1
        def mock_api_response(*args, **kwargs):
            nonlocal id_counter
            response_data = {
                'code': 0,
                'message': 'PC created',
                'objects': {f'PC::{id_counter}': {'key': f'PC::{id_counter}'}}
            }
            id_counter += 1
            return MagicMock(status_code=200, json=MagicMock(return_value=response_data))
        
        # Configurar el mock request para devolver diferentes IDs
        mock_request.side_effect = mock_api_response

        # Ejecutar la función insert
        insert()


        # Verificar los valores
        for computer in self.computers:
            self.assertTrue(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())
            self.assertTrue(SerialAndService.objects.filter(serial_number=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 0)

    # Test para validar el funcionamiento si las computadoras no se crean en el servicio
    @patch('api_rest.tasks.task_insert_data.requests.request')
    @patch('api_rest.tasks.task_insert_data.look')
    def test_insert_computer_error(self, mock_look, mock_request):

        def mock_api_response(*args, **kwargs):
            response_data = {
                'code': 0,
                'message': 'null',
            }
            return MagicMock(status_code=200, json=MagicMock(return_value=response_data))
        
        # Configurar el mock request para devolver diferentes IDs
        mock_request.side_effect = mock_api_response

        # Ejecutar la función insert
        insert()


        # Verificar los valores
        for computer in self.computers:
            self.assertFalse(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())
            self.assertFalse(SerialAndService.objects.filter(serial_number=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 4)   


    # Test para ver si actualizan las computadoras en el servicio
    @patch('api_rest.tasks.task_insert_data.requests.request')
    @patch('api_rest.tasks.task_insert_data.look')
    def test_update_computer(self, mock_look, mock_request):

        # Computadoras ya existentes
        mock_look.return_value = True

        id_counter = 1
        def mock_api_response(*args, **kwargs):
            nonlocal id_counter
            response_data = {
                'code': 0,
                'message': 'PC updated',
                'objects': {f'PC::{id_counter}': {'key': f'PC::{id_counter}'}}
            }
            id_counter += 1
            return MagicMock(status_code=200, json=MagicMock(return_value=response_data))
        
        # Configurar el mock request para devolver diferentes IDs
        mock_request.side_effect = mock_api_response

        # Ejecutar la función insert
        insert()


        # Verificar los datos
        for computer in self.computers:
            self.assertTrue(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 0)   