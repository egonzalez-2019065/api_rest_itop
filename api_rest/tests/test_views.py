from django.test import TestCase, Client
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from api_rest.models import Computer, HistorialComputer
from unittest.mock import patch, MagicMock
import base64
import os


class ComputerViewSetTest(TestCase):  
    def setUp(self):
        # Credenciales para el token de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        # Generar un token de acceso usando SimpleJWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)


    # Test para verificar que las computadoras se guardan de forma correcta
    def test_computer_post(self): 
        data = {
            "name": "DESKTOP-0540100",
            "organization_name": "Guate",
            "location_name": "Guate",
            "brand_name": "LENOVO",
            "model_name": "20TBS25V00",
            "osfamily_name": "Windows 11",
            "type": "Laptop",
            "cpu": "i5-1135G7 11th Gen Intel(R) @ 2.40GHz",
            "os_version_name": "23H2",
            "serialnumber": "PF33X100",
            "status": "Reserva",
            "ram": 16,
            "description": "La capacidad del disco es: 238 GB y le queda libre: 1.00 GB",
            "move2production": "2022-01-07",
            "purchase_date": "2022-01-07",
            "end_of_warranty": "2023-01-06"
        }
        # Consulta simulada para el post
        response = self.client.post(
            "/computers/", 
            data = data,
            content_type='application/json',
            HTTP_AUTHORIZATION = f'Bearer {self.access_token}'
        )

        # Comprobar que la consulta sea como se espera
        self.assertEqual(response.status_code, 201)
        created_computer = Computer.objects.get(serialnumber='PF33X100')
        self.assertEqual(created_computer.name, 'DESKTOP-0540100')
        self.assertEqual(created_computer.cpu, 'i5-1135G7 11th Gen Intel(R) @ 2.40GHz')


class ApiPeticionTest(TestCase): 
    def setUp(self): 
        # Credenciales para el token de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()

        # Computadora de prueba 
        self.computer = Computer.objects.create(
            name="DESKTOP-0540100",
            organization_name="Guate",
            location_name="Guate",
            brand_name="LENOVO",
            model_name="20TBS25V00",
            osfamily_name="Windows 11",
            type="Laptop",
            cpu="i5-1135G7 11th Gen Intel(R) @ 2.40GHz",
            os_version_name="23H2",
            serialnumber="PF33X100",
            status="Reserva",
            ram=16,
            description="La capacidad del disco es: 238 GB y le queda libre: 1.00 GB",
            move2production="2022-01-07",
            purchase_date="2022-01-07",
            end_of_warranty="2023-01-06"
        )

    def encode_credentials(self, username, password):
        credentials = f'{username}:{password}'
        return base64.b64encode(credentials.encode()).decode()
    
    '''
    # Test simulando que Itop confirma el ingreso de datos
    @patch('requests.post')
    def test_itop_peticion_check(self, mock_post): 
        # Configurar la respuesta simulada por Itop
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"1": "PF33X100"}
        mock_response.return_value = mock_response  

        # Codificar las credenciales
        econded_credentials = self.encode_credentials(
            os.getenv('USER_ITOP'),
            os.getenv('PASSWORD_ITOP')
        )
            
        response = self.client.post(
            "/api_peticion/",
            content_type = 'application/json',
        )

        expected_data = {
            "operation": "core/create",
            "class": "PC",
            "fields": {
                "hostname": "DESKTOP-0540100",
                "organization_name": "Guate",
                "location_name": "Guate",
                "brand_name": "LENOVO",
                "model_name": "20TBS25V00",
                "osfamily_name": "Windows 11",
                "type": "Laptop",
                "cpu": "i5-1135G7 11th Gen Intel(R) @ 2.40GHz",
                "os_version_name": "23H2",
                "serialnumber": "PF33X100",
                "status": "Reserva",
                "ram": 16,
                "description": "La capacidad del disco es: 238 GB y le queda libre: 1.00 GB",
                "move2production": "2022-01-07",
                "purchase_date": "2022-01-07",
                "end_of_warranty": "2023-01-06",
            }
        }

        # Comprobar que la respuesta sea la esperada
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Datos guardados exitosamente"})
        self.assertTrue(HistorialComputer.objects.filter(serialnumber="PF33X100").exists())
        self.assertFalse(Computer.objects.filter(serialnumber="PF33X100").exists())

        mock_post.assert_called_once_with(
            os.getenv('ITOP_URL'),
            json=expected_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Basic {econded_credentials}'
            }
        )
    '''

    # Test simulando que itop no permite el ingreso de los datos
    @patch('requests.post')
    def test_itop_peticion_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Error message from iTop"
        mock_post.return_value = mock_response

        encoded_credentials = self.encode_credentials(
            os.getenv('USER_ITOP'),
            os.getenv('PASSWORD_ITOP')
        )

        response = self.client.post(
            '/api_peticion/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Basic {encoded_credentials}'
        )

        print(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "Error al realizar la petición a Itop: Error message from iTop"})

        self.assertFalse(HistorialComputer.objects.filter(serialnumber="PF33X100").exists())
        self.assertTrue(Computer.objects.filter(serialnumber="PF33X100").exists())

