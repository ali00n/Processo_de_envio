
import config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Utilities:
    def __init__(self):
        self.wait_time = config.WAIT_TIME
        self.driver = None
        pass

    def scroll_by(self, driver, pixels):
        """Rola a página para baixo por um número específico de pixels."""
        driver.execute_script(f"window.scrollBy(0, {pixels});")

    def find_element_with_wait(self, by, value, timeout=None, parent=None):
        """Encontra um elemento esperando ele estar presente no DOM."""
        if timeout is None:
            timeout = self.wait_time

        if parent is None:
            parent = self.driver

        return WebDriverWait(parent, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def find_elements_with_wait(self, by, value, timeout=None, parent=None):
        """Encontra uma lista de elementos esperando eles estarem presentes no DOM."""
        if timeout is None:
            timeout = self.wait_time

        if parent is None:
            parent = self.driver

        return WebDriverWait(parent, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

