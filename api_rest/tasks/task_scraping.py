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
                    logger.info(" Iniciando el proceso de scrapping para obtener las fechas.")
                    # Configuración del navegador Firefox en modo headless
                    firefox_options = FirefoxOptions()
                    firefox_options.add_argument("--headless") # Ejecuta sin interfaz gráfica
                    
                    
                    # Inicializar el navegador
                    driver = webdriver.Firefox(options=firefox_options)
                    logger.info(" Abriendo el navegador de Firefox en modo headless.")

                    
                    # Navegar a la página de búsqueda de garantía de Lenovo
                    driver.get("https://pcsupport.lenovo.com/us/es/warranty-lookup#/")
                    logger.info(" Página de lenovo encontrada")

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
                    logger.info(" Fechas encontradas correctamente.")

                    # Verificar y guardar las fechas
                    if len(properties) >= 5:
                        start_date = properties[1].text.strip()
                        end_date = properties[4].text.strip()

                        logger.info(f" Fechas obtenidas: {start_date} - {end_date} desde la página")
                        data['move2production'] = start_date
                        data['purchase_date'] = start_date
                        data['end_of_warranty'] = end_date
                        async_task('api_rest.tasks.task_clean_data.clear', data)
                        logging.info(" Proceso para obtener las fechas realizado correctamente.")

                    else:
                        async_task('api_rest.tasks.task_clean_data.clear', data)
                        logging.error(" No se encontraron suficientes elementos de propiedad, data procesada sin fechas.")

                except Exception as e:
                    async_task('api_rest.tasks.task_clean_data.clear', data)
                    logging.error(f" No se puedo realizar el proceso para obtener las fechas: {e}, data procesada sin fechas.")
                finally:
                    if driver:
                        driver.quit()
            else: 
                logging.error(" La computadora no era de la marca esperada, data procesada sin fechas.")
                async_task('api_rest.tasks.task_clean_data.clear', data)

        else: 
            logging.info(" La computadora ya existe en el servicio, se saltó el proceso para obtener las fechas.")
            async_task('api_rest.tasks.task_clean_data.clear', data)
