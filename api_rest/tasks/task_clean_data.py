from api_rest.models import Computer
from dotenv import load_dotenv
from urllib.parse import urlencode
import json
import requests 
import os
import base64
import re
import logging

# Variables de env
load_dotenv()

# Configuración para los logs 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para hacer las diferentes peticiones según los datos del diccionario: data
def pattern(class_name, look_to, field_value):
    url = os.getenv('SERVICE_URL') 
    us = os.getenv('USER_SERVICE')
    pas = os.getenv('PASSWORD_SERVICE')
    # Codificación de las credenciales
    credentials = f'{us}:{pas}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Preparación de los headers para la petición
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }

    # Petición según las necesidades
    simple_data = {
        "operation": "core/get",
        "class": f"{class_name}",
        "key": f"SELECT {class_name} WHERE {look_to} = '{field_value}'",
        "output_fields": "name",
        "limit": 1,
    }

    # Convertirlo a JSON  
    json_data = json.dumps(simple_data)

    # Preparando la URL para la solicitud 
    encoded_json_data = urlencode({'json_data': json_data}) 
    url_base = f"{url}&{encoded_json_data}"
    
    # Solicitud al API  
    response = requests.request("POST", url_base, headers=headers)

    # Convirtiendo en json la respuesta
    response_json = response.json()
    if response.status_code == 200: 
        if response_json['code'] == 0:

            # Buscarlo en la cadena de texto
            response_str = str(response_json)
            er = f"{class_name}::(\\d+)"
            id = re.search(er, response_str)
            if id: 
                # ID extraído
                id_final = id.group(1)
                return id_final
            
# Función para obtener los valores reales según el API 
def clear(data):
    
    # Obtener el dato de la locación
    if data.get('location_id'):
        # upper para no sufrir casos por el case sensitive
        loupper = data.get('organization_id').upper()
        match loupper:
            case "ESTADOS UNIDOS":
                location_id = pattern('Location', 'name', 'Default')
            case "GUATEMALA":
                location_id = pattern('Location', 'name', 'Default')
            case "EL SALVADOR":
                location_id = pattern('Location', 'org_name', data['organization_id'])
            case "HONDURAS":
                location_id = pattern('Location', 'org_name', data['organization_id'])
            case "NICARAGUA":
                location_id = pattern('Location', 'org_name', data['organization_id'])
            case "COSTA RICA":
                location_id = pattern('Location', 'name', 'Default') 
            case _:
                location_id = pattern('Location', 'name', 'Default')

        # Settear el dato según el case
        if location_id:
            data['location_id'] = location_id
        else:
            data['location_id'] = None

    # Obtener el dato de la organización
    if data.get('organization_id'):
        organization_id = pattern('Organization', 'name', data['organization_id'])
        if organization_id:
            data['organization_id'] = organization_id
        else:
            data['organization_id'] = None
    
    # Obtener el dato de la marca
    if data.get('brand_id'):
        brand_id = pattern('Brand', 'name', data['brand_id'])
        if brand_id:
            data['brand_id'] = brand_id
        else:
            data['brand_id'] = None
    
    # Obtener el dato del modelo
    if data.get('model_id'):
        model_id = pattern('Model', 'name', data['model_id'])
        if model_id:
            data['model_id'] = model_id
        else:
            data['model_id'] = None
    
    # Obtener el dato del OS
    if data.get('osfamily_id'):
        system = pattern('OSFamily', 'name', data['osfamily_id'])
        if system:
            data['osfamily_id'] = system
        else:
            data['osfamily_id'] = None
    
    # Obtener el dato de la versión del OS 
    if data.get('os_version_id'):
        version = pattern('OSVersion', 'name', data['os_version_id'])
        if version:
            data['os_version_id'] = version
        else:
            data['os_version_id'] = None

    # Guardar el equipo con la data setteada 
    Computer.objects.get_or_create(
       serialnumber = data['serialnumber'],
        defaults={
            'name': data.get('name'), 
            'organization_id': data.get('organization_id'),
            'location_id': data.get('location_id'), 
            'brand_id': data.get('brand_id'),
            'model_id': data.get('model_id'),
            'osfamily_id': data.get('osfamily_id'),
            'type': data.get('type'),
            'cpu': data.get('cpu'),
            'os_version_id': data.get('os_version_id'),
            'status': data.get('status'),
            'ram': data.get('ram'),
            'description': data.get('description'),
            'move2production': data.get('move2production'),
            'purchase_date': data.get('purchase_date'),
            'end_of_warranty': data.get('end_of_warranty'),
        }
    )
    logger.info(f' El equipo {data['serialnumber']} procesado y guardado efectivamente.')
