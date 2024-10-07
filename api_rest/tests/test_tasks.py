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
    def setUp(self):
            self.computers = [
            Data.objects.create(
                serialnumber='PF33XE44',
                name='DESKTOP-0540NH8',
                organization_id='',
                location_id='',
                brand_id='LENOVO',
                model_id='20TBS25V00',
                osfamily_id='Windows 11',
                os_version_id='11 Business',
                type='',
                cpu='i5-1135G7 11th Gen Intel(R) @ 2.40GHz',
                ram=8,
                status='production',
                description='La capacidad del disco es: 238 GB y le queda libre: 0.16 GB',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
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
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),

            Data.objects.create(
                serialnumber='PF33X005',
                name='Nicaragua Computer',
                organization_id='nicaragua',
                location_id='nicaragua',
                brand_id='Lenovo',
                model_id='Thinkpad',
                osfamily_id='Windows',
                os_version_id='Pro 10',
                type='desktop',
                cpu='Intel i5',
                ram=8,
                status='production',
                description='500 GB y 100 disponibles',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),

            Data.objects.create(
                serialnumber='PF33X006',
                name='Guatemala Computer',
                organization_id='guatemala',
                location_id='guatemala',
                brand_id='HP',
                model_id='Elitebook',
                osfamily_id='Windows',
                os_version_id='Pro 11',
                type='laptop',
                cpu='Intel i7',
                ram=16,
                status='production',
                description='1 TB y 500 disponibles',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),

            Data.objects.create(
                serialnumber='PF33X007',
                name='USA Computer',
                organization_id='estados unidos',
                location_id='estados unidos',
                brand_id='Dell',
                model_id='Latitude',
                osfamily_id='Linux',
                os_version_id='Ubuntu 22.04',
                type='laptop',
                cpu='Intel i9',
                ram=32,
                status='production',
                description='2 TB y 1 TB disponibles',
                move2production='2024-01-01',
                purchase_date='2024-01-01',
                end_of_warranty='2025-01-01'
            ),

            Data.objects.create(
                serialnumber='PF33X008',
                name='El Salvador Advanced Computer',
                organization_id='el salvador',
                location_id='el salvador',
                brand_id='Asus',
                model_id='Zenbook',
                osfamily_id='Windows',
                os_version_id='Pro 11',
                type='laptop',
                cpu='Intel i5',
                ram=8,
                status=None,
                description=None,
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
        ]
    def test_task_clear(self):
        # Llamada a la función que limpia la data original y transfiere a PComputer
        clear()
        
        # Verificar que todas las computadoras hayan sido eliminadas de Data y estén en PComputer
        for computer in self.computers[:5]:
            self.assertIsNone(Data.objects.filter(serialnumber=computer.serialnumber).first())
            self.assertIsNotNone(PComputer.objects.filter(serialnumber=computer.serialnumber).first())
            self.assertEqual(PComputer.objects.get(serialnumber=computer.serialnumber).name, computer.name)
        self.assertEqual(PComputer.objects.count(), 5)



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
                serialnumber='PF33XE44',
                name='DESKTOP-0540NH8',
                organization_id='',
                location_id='',
                brand_id='LENOVO',
                model_id='20TBS25V00',
                osfamily_id='Windows 11',
                os_version_id='11 Business',
                type='',
                cpu='i5-1135G7 11th Gen Intel(R) @ 2.40GHz',
                ram=8,
                status='production',
                description='La capacidad del disco es: 238 GB y le queda libre: 0.16 GB',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
            PComputer.objects.create(
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
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),

            PComputer.objects.create(
                serialnumber='PF33X005',
                name='Nicaragua Computer',
                organization_id='nicaragua',
                location_id='nicaragua',
                brand_id='Lenovo',
                model_id='Thinkpad',
                osfamily_id='Windows',
                os_version_id='Pro 10',
                type='desktop',
                cpu='Intel i5',
                ram=8,
                status='production',
                description='500 GB y 100 disponibles',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
            PComputer.objects.create(
                serialnumber='PF33X006',
                name='Guatemala Computer',
                organization_id='guatemala',
                location_id='guatemala',
                brand_id='HP',
                model_id='Elitebook',
                osfamily_id='Windows',
                os_version_id='Pro 11',
                type='laptop',
                cpu='Intel i7',
                ram=16,
                status='production',
                description='1 TB y 500 disponibles',
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
            PComputer.objects.create(
                serialnumber='PF33X007',
                name='USA Computer',
                organization_id='estados unidos',
                location_id='estados unidos',
                brand_id='Dell',
                model_id='Latitude',
                osfamily_id='Linux',
                os_version_id='Ubuntu 22.04',
                type='laptop',
                cpu='Intel i9',
                ram=32,
                status='production',
                description='2 TB y 1 TB disponibles',
                move2production='2024-01-01',
                purchase_date='2024-01-01',
                end_of_warranty='2025-01-01'
            ),
            PComputer.objects.create(
                serialnumber='PF33X008',
                name='El Salvador Advanced Computer',
                organization_id='el salvador',
                location_id='el salvador',
                brand_id='Asus',
                model_id='Zenbook',
                osfamily_id='Windows',
                os_version_id='Pro 11',
                type='laptop',
                cpu='Intel i5',
                ram=8,
                status=None,
                description=None,
                move2production=None,
                purchase_date=None,
                end_of_warranty=None
            ),
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
        for computer in self.computers[:5]:
            self.assertTrue(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())
            self.assertTrue(SerialAndService.objects.filter(serial_number=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 1)

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
        for computer in self.computers[:5]:
            self.assertFalse(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())
            self.assertFalse(SerialAndService.objects.filter(serial_number=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 6)   


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
        for computer in self.computers[:5]:
            self.assertTrue(HistorialPComputer.objects.filter(serialnumber=computer.serialnumber).exists())

        self.assertEqual(PComputer.objects.count(), 1)   