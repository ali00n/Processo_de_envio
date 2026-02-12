
import config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import logging

logger = logging.getLogger(__name__)

class Utilities:
    def __init__(self, driver):
        self.driver = driver
        self.wait_time = config.WAIT_TIME

    def scroll_by(self, pixels):
        """Rola a página para baixo por um número específico de pixels."""
        if self.driver:
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")

    def find_element_with_wait(self, by, value, timeout=None):
        """Encontra um elemento esperando ele estar presente no DOM."""
        if timeout is None:
            timeout = self.wait_time

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.error(f"Elemento não encontrado (Tempo esgotado): {by}={value}")
            raise

    def find_elements_with_wait(self, by, value, timeout=None):
        """Encontra uma lista de elementos esperando eles estarem presentes no DOM."""
        if timeout is None:
            timeout = self.wait_time

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            logger.warning(f"Elementos não encontrados (Tempo esgotado): {by}={value}")
            return []

    def find_element_clickable(self, by, value, timeout=None):
        """Encontra um elemento esperando ele estar clicável."""
        if timeout is None:
            timeout = self.wait_time

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            logger.error(f"Elemento não clicável (Tempo esgotado): {by}={value}")
            raise

