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
logger = logging.getLogger(__name__)

def put_dates(computer):
    # Yendo a buscar en el servicio al equipo
    if computer.serialnumber != "":
        look_response = look(computer.serialnumber)
    
    if not look_response:
        if (computer.brand_id == 9) and computer.serialnumber != "":
            driver = None
            try:
                logger.info(f"Iniciando el proceso de scrapping para el equipo {computer.serialnumber} para obtener las fechas.")
                # Configuración del navegador Firefox en modo headless
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
                
                # Inicializar el navegador
                driver = webdriver.Firefox(options=firefox_options)
                logger.info("Abriendo el navegador de Firefox en modo headless.")

                # Navegar a la página de búsqueda de garantía de Lenovo
                driver.get("https://pcsupport.lenovo.com/us/es/warranty-lookup#/") 
                logger.info("Página de Lenovo encontrada")

                # Esperar y encontrar el campo de entrada
                wait = WebDriverWait(driver, 10)
                serial_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.button-placeholder__input")))

                # Ingresar el número de serie y enviar
                serial_input.send_keys(computer.serialnumber)
                serial_input.send_keys(Keys.RETURN)

                # Esperar a que la página cargue la información
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.property-value")))

                # Obtener las fechas de garantía
                properties = driver.find_elements(By.CSS_SELECTOR, "span.property-value")
                logger.info("Fechas encontradas correctamente.")

                # Verificar y guardar las fechas
                if len(properties) >= 5:
                    start_date = properties[1].text.strip()
                    end_date = properties[4].text.strip()

                    logger.info(f"Fechas obtenidas: {start_date} - {end_date} para el equipo {computer.serialnumber} desde la página")
                    logger.info("Proceso para obtener las fechas realizado correctamente.")
                    return start_date, end_date
                else:
                    logger.error("No se encontraron suficientes elementos de propiedad, data procesada sin fechas.")
                    return None, None
            except Exception as e:
                logger.error(f"No se pudo realizar el proceso para obtener las fechas: {e}, data procesada sin fechas.")
                return None, None
            finally:
                if driver:
                    driver.quit()
        else: 
            logger.error("El equipo no era de la marca esperada, data procesada sin fechas.")
            return None, None
    else: 
        logger.info(f"El equipo {computer.serialnumber} ya existe en el servicio, se saltó el proceso para obtener las fechas.")
        return None, None
