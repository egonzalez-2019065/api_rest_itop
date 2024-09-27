from django.test import TestCase, Client
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from api_rest.models import Computer


class ComputerViewSetTest(TestCase):  
    def setUp(self):
        # Credenciales para el token de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        # Generar un token de acceso usando SimpleJWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
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
            'move2production':'2024-01-01',
            'purchase_date': '2024-01-01',
            'end_of_warranty': '2025-01-01'
        }


    # Test para verificar que las computadoras se guardan de forma correcta
    def test_puter_post(self): 
        # Consulta simulada para el post
        response = self.client.post(
            "/computers/", 
            data = self.data,
            content_type='application/json',
            HTTP_AUTHORIZATION = f'Bearer {self.access_token}',
        )

        # Comprobar que la computadora se haya agregado correctamente
        self.assertEqual(response.data['message'], 'Equipo creado exitosamente')
        self.assertEqual(response.status_code, 201)
    
    def test_update_computer(self):
        Computer.objects.create(
            serialnumber='PF33X004',
            name='Test Computer',
            organization_id='el salvador',
            location_id=1,
            brand_id=1,
            model_id=1,
            osfamily_id=1,
            os_version_id=1,
            type='desktop',
            cpu='Intel i7',
            ram=16,
            status='active',
            description='A test computer',
            move2production='2024-01-01',
            purchase_date='2024-01-01',
            end_of_warranty='2025-01-01',
        )

        response = self.client.post(
            "/computers/", 
            data = self.data,
            content_type='application/json',
            HTTP_AUTHORIZATION = f'Bearer {self.access_token}',
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Equipo actualizado correctamente')
        self.assertIsNotNone(Computer.objects.filter(serialnumber = 'PF33X004').first())
        self.assertEqual(Computer.objects.get().serialnumber, 'PF33X004')
        self.assertEqual(Computer.objects.get().name, 'Test Computer')
        