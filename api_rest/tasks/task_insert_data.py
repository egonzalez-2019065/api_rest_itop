

import base64
import json
import logging
import os
import re
from urllib.parse import urlencode
import requests

from api_rest.models import Computer, HistorialComputer, SerialANDIdService

# Configuración para los logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def look(sn):
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
           logger.error(" No hay computadoras para procesar.")

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
            url_service = os.getenv('SERVICE_URL') 
            username = os.getenv('USER_SERVICE')
            password = os.getenv('PASSWORD_SERVICE')

            # Codificación de las credenciales
            credentials = f'{username}:{password}'
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Preparación de los headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }

            # Enviar la url completa 
            url_base = f"{url_service}&{encoded_json_data}"
            
            # Enviar la petición al Servicio
            try:
                response = requests.request("POST", url_base, headers=headers)

                # Convierte la respuesta a un json
                service_response = response.json()

                # Validación de la respuesta general del servicio
                if response.status_code == 200:

                    # Guardar la computadora con el ID que devuelva el servicio
                    # Convetir el diccionario a cadena de texto
                    service_response_str = str(service_response)

                    # Buscarlo en la cadena de texto
                    service_id_match = re.search(r'PC::(\d+)', service_response_str)

                    # ID extraído
                    service_id_final = service_id_match.group(1)

                    # Guarda el id de la respuesta del servicio y el número de serie
                    serial_number_instance, created = SerialANDIdService.objects.get_or_create(
                        serial_number=computer.serialnumber,  # Buscar por el número de serie
                        defaults = {
                            'id_service': service_id_final  # Si no existe, crear con este id_service
                        }
                    )

                    # Validación más detallada según el error que devuelva el servicio
                    if service_response['code'] == 0: 

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
                        if 'created' in service_response_str:
                            logger.info(f" Computadora {computer.serialnumber} fue agregada correctamente en el servicio.")
                        else:
                            logger.info(f" Computadora {computer.serialnumber} fue actualizada correctamente en el servicio.")

                    else:
                        logger.error(f" Error al intentar agregar {computer.serialnumber}, {service_response['message']} código: {service_response['code']}")
                else: 
                    logger.error(f" Error al intentar agregar {computer.serialnumber}, {response.text} código: {response.status_code}")
            except requests.RequestException as req_err:
                logger.error(f" Error al realizar la petición para {computer.serialnumber}: {req_err}")
            except Exception as e:
                logger.error(f" Error fatal para {computer.serialnumber}: {e}, la API responde: {service_response['message']}")   


