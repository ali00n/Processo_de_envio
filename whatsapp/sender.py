# whatsapp/sender.py
import urllib.parse
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import config

logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self, browser_manager):
        """
        Classe responsável por enviar mensagens via WhatsApp Web.
        :param browser_manager: Instância de BrowserManager.
        """
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()

    def formatar_mensagem(self, info: dict) -> str:
        """Monta mensagem final para envio no WhatsApp."""
        return f"Hoje temos aula de {info.get('disciplina')} — tema: {info.get('tema')}"

    def enviar_whatsapp_via_selenium(self, phone: str, mensagem: str):
        """
        Envia mensagem pelo WhatsApp Web (precisa estar logado no QR Code).
        :param phone: Número no formato DDI+DDD+número. Ex: 5511999999999
        :param mensagem: Texto da mensagem.
        """
        try:
            msg_encoded = urllib.parse.quote(mensagem)
            url = f"{config.WHATSAPP_WEB_URL}?phone={phone}&text={msg_encoded}"

            self.driver.get(url)

            # Aguarda o botão de envio
            send_btn = WebDriverWait(self.driver, config.WAIT_TIME).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar']"))
            )
            send_btn.click()

            logger.info(f"Mensagem enviada para {phone}: {mensagem}")
            time.sleep(2) # Dar um tempo para o envio processar

        except TimeoutException:
            logger.error("Não foi possível enviar a mensagem: botão de enviar não encontrado ou tempo esgotado.")
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
