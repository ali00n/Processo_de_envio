# browser/manager.py
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


import config

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        """Inicializa o gerenciador do navegador."""
        self.driver = None
        self.wait_time = config.WAIT_TIME
        self._setup_driver()

    def _setup_driver(self):
        """Configura o ChromeDriver com as opções definidas em config.py."""
        options = webdriver.ChromeOptions()

        if config.HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Configurar pasta de download
        prefs = {
            "download.default_directory": config.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("ChromeDriver iniciado com sucesso.")

    def get_driver(self):
        """Retorna a instância do driver."""
        return self.driver

    def close(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
            logger.info("Navegador fechado.")
