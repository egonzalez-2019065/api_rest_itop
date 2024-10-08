from api_rest.models import Data, PComputer
from dotenv import load_dotenv
from urllib.parse import urlencode
import json
import requests 
import os
import base64
import re
import logging

from api_rest.tasks.task_scraping import put_dates 

# Variables de env
load_dotenv()

# Configuración para los logs 
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

    # Verifica el código de estado de la respuesta
    if response.status_code == 200:
        try:
            # Convirtiendo en json la respuesta
            response_json = response.json()
            if response_json['code'] == 0:
                # Buscarlo en la cadena de texto
                response_str = str(response_json)
                er = f"{class_name}::(\\d+)"
                id = re.search(er, response_str)
                if id: 
                    # ID extraído
                    id_final = id.group(1)
                    return id_final
            else:
                logger.warning('No fue posible manejar la respuesta del API')
                return None
        except ValueError:
            logger.error(f"Respuesta del API: {response.text}")
            return None
    else:
        logger.error(f"Error en la solicitud al API: {response.status_code} - {response.text}")
        return None
                        
# Función para obtener los valores reales según el API 
def clear():
    computersData = Data.objects.filter()[:5]
    if not computersData.exists():
            logger.warning("El proceso de limpieza de datos no fue iniciado, no hay registros.")
    for computer in computersData:
        # Obtener el dato de la locación
        if computer.location_id:
            # upper para no sufrir casos por el case sensitive  
            loupper = computer.organization_id.upper()
            match loupper:
                case "ESTADOS UNIDOS":
                    location_id = pattern('Location', 'name', 'Default')
                case "GUATEMALA":
                    location_id = pattern('Location', 'name', 'Default')
                case "EL SALVADOR":
                    location_id = pattern('Location', 'org_name', computer.organization_id)
                case "HONDURAS":
                    location_id = pattern('Location', 'org_name', computer.organization_id)
                case "NICARAGUA":
                    location_id = pattern('Location', 'org_name', computer.organization_id)
                case "COSTA RICA":
                    location_id = pattern('Location', 'name', 'Default') 
                case _:
                    location_id = pattern('Location', 'name', 'Default')

            # Settear el dato según el case
            computer.location_id = location_id if location_id else None

        # Obtener el dato de la organización
        if computer.organization_id:
            organization_id = pattern('Organization', 'name', computer.organization_id)
            computer.organization_id = organization_id if organization_id else None
        
        # Obtener el dato de la marca
        if computer.brand_id:
            brand_id = pattern('Brand', 'name', computer.brand_id)
            computer.brand_id = brand_id if brand_id else None
        
        # Obtener el dato del modelo
        if computer.model_id:
            model_id = pattern('Model', 'name', computer.model_id)
            computer.model_id = model_id if model_id else None
        
        # Obtener el dato del OS
        if computer.osfamily_id:
            system = pattern('OSFamily', 'name', computer.osfamily_id)
            computer.osfamily_id = system if system else None
        
        # Obtener el dato de la versión del OS 
        if computer.os_version_id:
            version = pattern('OSVersion', 'name', computer.os_version_id)
            computer.os_version_id = version if version else None


        # Realiza el proceso de scraping
        start_date, end_date = put_dates(computer)

         # Asignar las fechas al objeto computer
        if start_date and end_date:
            computer.move2production = start_date
            computer.purchase_date = start_date 
            computer.end_of_warranty = end_date

        # Guardar el equipo con la data setteada 
        PComputer.objects.update_or_create(
            serialnumber=computer.serialnumber,
            defaults={
                'name': computer.name, 
                'organization_id': computer.organization_id,
                'location_id': computer.location_id, 
                'brand_id': computer.brand_id,
                'model_id': computer.model_id,
                'osfamily_id': computer.osfamily_id,
                'type': computer.type,
                'cpu': computer.cpu,
                'os_version_id': computer.os_version_id,
                'status': computer.status,
                'ram': computer.ram,
                'description': computer.description,
                'move2production': computer.move2production,
                'purchase_date': computer.purchase_date,
                'end_of_warranty': computer.end_of_warranty,
            }
        )
        computer.delete()
        logger.info(f'El equipo {computer.serialnumber} fue procesado y guardado efectivamente.')
