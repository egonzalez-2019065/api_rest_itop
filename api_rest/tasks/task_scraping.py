from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django_q.tasks import async_task
from api_rest.tasks.task_insert_data import look
import logging


# Configuración para los logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def put_dates(data):
        # Yendo a buscar en el servicio al equipo
        if data.get('serialnumber')!= "":
            look_response = look(data.get('serialnumber'))
        
        if not look_response:
            if (data.get('brand_id') == "LENOVO" or data.get('brand_id') == "Lenovo") and data.get('serialnumber')!= "":
                driver = None
                try:
                    logging.info("Iniciando el proceso de scrapping para obtener las fechas")
                    # Configuración del navegador Firefox en modo headless
                    firefox_options = FirefoxOptions()
                    firefox_options.add_argument("--headless") # Ejecuta sin interfaz gráfica
                    
                    # Inicializar el navegador
                    driver = webdriver.Firefox(options=firefox_options)
                    logging.info("Abriendo el navegador Firefox en modo headless")

                    
                    # Navegar a la página de búsqueda de garantía de Lenovo
                    driver.get("https://pcsupport.lenovo.com/us/es/warranty-lookup#/")
                    logging.info("Página de lenovo encontrada")

                    # Esperar y encontrar el campo de entrada
                    wait = WebDriverWait(driver, 10)
                    serial_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.button-placeholder__input")))

                    # Ingresar el número de serie y enviar
                    serial_input.send_keys(data.get('serialnumber'))
                    serial_input.send_keys(Keys.RETURN)

                    # Esperar a que la página cargue la información
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.property-value")))

                    # Obtener las fechas de garantía
                    properties = driver.find_elements(By.CSS_SELECTOR, "span.property-value")
                    logging.info("Fechas encontradas")

                    # Verificar y guardar las fechas
                    if len(properties) >= 5:
                        start_date = properties[1].text.strip()
                        end_date = properties[4].text.strip()

                        logging.info(f"Fechas obtenidas: {start_date} - {end_date} de forma correcta")
                        data['move2production'] = start_date
                        data['purchase_date'] = start_date
                        data['end_of_warranty'] = end_date
                        print(data)
                        async_task('api_rest.tasks.task_clean_data.clear', data)
                    else:
                        async_task('api_rest.tasks.task_clean_data.clear', data)
                        logging.error("No se encontraron suficientes elementos de propiedad.")
                        print('entró al else')

                except Exception as e:
                    async_task('api_rest.tasks.task_clean_data.clear', data)
                    logging.error(f"Error obteniendo las fechas {e}")
                    print('entró en error')
                finally:
                    async_task('api_rest.tasks.task_clean_data.clear', data)
                    if driver:
                        driver.quit()
            else: 
                logging.error("La computadora no era de la marca esperada")
                async_task('api_rest.tasks.task_clean_data.clear', data)

        else: 
            async_task('api_rest.tasks.task_clean_data.clear', data)


