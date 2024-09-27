from api_rest.models import Computer, HistorialComputer, SerialAndIDItop
from dotenv import load_dotenv
from urllib.parse import urlencode
from rest_framework.response import Response
import json
import requests 
import os
import base64
import re
import logging
from django_q.tasks import Schedule

# Variables de env
load_dotenv()

# Configuración para los logs 
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Función para hacer las diferentes peticiones según los datos del diccionario
def pattern(class_name, look_to, field_value):
    url = os.getenv('ITOP_URL') 
    us = os.getenv('USER_ITOP')
    pas = os.getenv('PASSWORD_ITOP') 

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
    logger.info(response.text)

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
    equipo = Computer.objects.get_or_create(
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
    logger.info(f'Equipo limpiado y guardado efectivamente: {data['serialnumber']}')


def look(sn):
    url = os.getenv('ITOP_URL') 
    us = os.getenv('USER_ITOP')
    pas = os.getenv('PASSWORD_ITOP') 

    # Codificación de las credenciales
    credentials = f'{us}:{pas}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Preparación de los headers para la petición
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }

    # Petición para saber si existe en el servicio
    simple_data = {
        "operation": "core/get",
        "class": "PC",
        "key": f"SELECT PC WHERE serialnumber = '{sn}'",
        "output_fields": "name"
    }

    # Convertirlo a JSON  
    json_data = json.dumps(simple_data)

    # Preparando la URL para la solicitud 
    encoded_json_data = urlencode({'json_data': json_data}) 
    url_base = f"{url}&{encoded_json_data}"
    
    # Solicitud al API  
    response = requests.request("POST", url_base, headers=headers)
    logger.info(response.text)

    # Convirtiendo en json la respuesta
    response_json = response.json()
    if response.status_code == 200: 
        if response_json['code'] == 0:
            if response_json['message'] != "Found: 1":
                return False
            else:
                return True


def insert(): 
        # Obtener todas las computadoras
        computers = Computer.objects.all()

        if not computers.exists():
           logger.error('No hay computadoras para procesar')

        for computer in computers:
            # Preparando los datos extraídos
            fields = {
                    "name": computer.name,
                    "description": computer.description,
                    "org_id": computer.organization_id or 15,
                    "move2production": computer.move2production.strftime("%Y-%m-%d") if computer.move2production else None,
                    "serialnumber": computer.serialnumber,
                    "location_id": computer.location_id or 8,
                    "status": computer.status,
                    "brand_id": computer.brand_id or 104,
                    "model_id": computer.model_id or 105,
                    "purchase_date": computer.purchase_date.strftime("%Y-%m-%d") if computer.purchase_date else None,
                    "end_of_warranty": computer.end_of_warranty.strftime("%Y-%m-%d") if computer.end_of_warranty else None,
                    "osfamily_id": computer.osfamily_id or 106,
                    "osversion_id": computer.os_version_id or 107,
                    "cpu": computer.cpu,
                    "ram": computer.ram,
                    "type": computer.type
                }
            # Decidiendo si actualizará o agregará la computadora
            exist = look(computer.serialnumber)
            data = None
            if exist:
                data = {
                    "operation": "core/update",
                    "class": "PC",
                    "comment": "Computadora actualizada desde el API",
                    "key": f"SELECT PC WHERE serialnumber = '{computer.serialnumber}'"
                }
            else: 
                data = {
                    "operation": "core/create",
                    "class": "PC",
                    "comment": "Computadora agregada desde el API",  
                    "output_fields": "name"
                }
            
            data["fields"] = fields
        
            # Convertirlo a JSON
            json_data = json.dumps(data)

            # Preparando la URL  
            encoded_json_data = urlencode({'json_data': json_data})

            # Preparación de las credenciales para agregarlas a los headers
            itop_url = os.getenv('ITOP_URL')
            username = os.getenv('USER_ITOP')
            password = os.getenv('PASSWORD_ITOP')

            # Codificación de las credenciales
            credentials = f'{username}:{password}'
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Preparación de los headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }

            # Enviar la url completa 
            url_base = f"{itop_url}&{encoded_json_data}"
            
            # Enviar la petición a iTop
            try:
                response = requests.request("POST", url_base, headers=headers)
                print(f'Respuesta Itop: {response.text}')

                # Convierte la respuesta a un json
                itop_response = response.json()

                # Validación de la respuesta general de Itop
                if response.status_code == 200:

                    # Guardar la computadora con el ID que devuelva Itop
                    # Convetir el diccionario a cadena de texto
                    itop_response_str = str(itop_response)

                    # Buscarlo en la cadena de texto
                    itop_id_match = re.search(r'PC::(\d+)', itop_response_str)

                    # ID extraído
                    itop_id_final = itop_id_match.group(1)

                    # Guarda el id de la respuesta de Itop y el número de serie
                    serial_number_instance, created = SerialAndIDItop.objects.get_or_create(
                        serial_number=computer.serialnumber,  # Buscar por el número de serie
                        defaults = {
                            'id_itop': itop_id_final  # Si no existe, crear con este id_itop
                        }
                    )

                    # Validación más detallada según el error que devuelva Itop
                    if itop_response['code'] == 0: 

                        # Procesar respuesta exitosa
                        historial_computer, created = HistorialComputer.objects.get_or_create(
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
                            })
                        if not created:
                            historial_computer.name = computer.name
                            historial_computer.organization_id = computer.organization_id
                            historial_computer.location_id = computer.location_id
                            historial_computer.brand_id = computer.brand_id
                            historial_computer.model_id = computer.model_id
                            historial_computer.osfamily_id = computer.osfamily_id
                            historial_computer.type = computer.type
                            historial_computer.cpu = computer.cpu
                            historial_computer.os_version_id = computer.os_version_id
                            historial_computer.status = computer.status
                            historial_computer.ram = computer.ram
                            historial_computer.description = computer.description
                            historial_computer.move2production = computer.move2production
                            historial_computer.purchase_date = computer.purchase_date
                            historial_computer.end_of_warranty = computer.end_of_warranty
                            historial_computer.save()

                        # Eliminar la computadora procesada
                        computer.delete()
                        print(itop_response_str)
                        if 'created' in itop_response_str:
                            logger.info(f"Computadora {computer.serialnumber} fue agregada correctamente")
                        else:
                            logger.info(f"Computadora {computer.serialnumber} fue actualizada correctamente")

                    else:
                        logger.error(f"Error al procesar {computer.serialnumber}, {itop_response['message']} código: {itop_response['code']}")
                else: 
                    logger.error(f"Error al procesar {computer.serialnumber}, {response.text} código: {response.status_code}")
            except requests.RequestException as req_err:
                logger.error(f"Error al realizar la petición para {computer.serialnumber}: {req_err}")
            except Exception as e:
                logger.error(f"Error fatal para {computer.serialnumber}: {e}, la API responde: {itop_response['message']}")   

