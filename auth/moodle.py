# auth/moodle.py
import time
import logging
from selenium.webdriver.common.by import By
from utilities.utilities import Utilities
import config

logger = logging.getLogger(__name__)

class MoodleAuth:
    def __init__(self, browser_manager):
        """
        Classe responsável pela autenticação no Moodle.
        :param browser_manager: Instância de BrowserManager.
        """
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()
        self.utilities = Utilities(self.driver)

    def login(self):
        """Realiza login no Moodle."""
        logger.info("Iniciando login no Moodle...")
        self.driver.get(config.MOODLE_LOGIN_URL)

        # Esperar carregar a página
        self.utilities.find_element_with_wait(By.ID, "username")
        logger.info("Página do Moodle carregada.")

        self.driver.find_element(By.XPATH, "//input[contains(@id, 'username')]").send_keys(config.USER)
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//input[contains(@id, 'password')]").send_keys(config.PASSWORD)
        time.sleep(1)
        self.utilities.find_element_clickable(By.XPATH, "//button[contains(text(), 'Acessar')]").click()
        time.sleep(1)
