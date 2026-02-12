# whatsapp/sender.py
import urllib.parse
import logging
import time
from selenium.webdriver.common.by import By
from utilities.utilities import Utilities
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
        self.utilities = Utilities(self.driver)

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
            send_btn = self.utilities.find_element_clickable(By.XPATH, "//button[@aria-label='Enviar']")
            send_btn.click()

            logger.info(f"Mensagem enviada para {phone}: {mensagem}")
            time.sleep(2) # Dar um tempo para o envio processar

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")

    def enviar_arquivo(self, phone: str, arquivo_path: str):
        """
        Envia um arquivo (documento/imagem) pelo WhatsApp Web.
        :param phone: Número no formato DDI+DDD+número.
        :param arquivo_path: Caminho absoluto do arquivo.
        """
        import os
        if not os.path.exists(arquivo_path):
            logger.error(f"Arquivo não encontrado: {arquivo_path}")
            return

        try:
            # 1. Abrir conversa (Isso já carrega a interface de chat)
            # Nota: Se já estiver na conversa, o get(url) recarrega a página. Idealmente, verificar se já está na conversa.
            # Mas seguindo o padrão simples:
            self.enviar_whatsapp_via_selenium(phone, f"Enviando arquivo: {os.path.basename(arquivo_path)}")
            time.sleep(2)

            # 2. Clicar no botão de anexo (Clip)
            # O seletor do clip pode mudar. Geralmente é um span ou div com title ou label específicos.
            # Tentativa genérica por XPATH de ícone mais ou clip
            clip_btn = self.utilities.find_element_clickable(By.XPATH, "//div[@title='Anexar'] | //span[@data-icon='plus']")
            clip_btn.click()
            time.sleep(1)

            # 3. Enviar caminho para o input de arquivo (input type='file')
            # O input geralmente está escondido. Não usamos click(), usamos send_keys().
            # O input para Documentos e Imagens pode ser o mesmo ou específico.
            # Procurar input genérico de arquivo
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(arquivo_path)
            time.sleep(2) # Esperar preview/upload

            # 4. Clicar em Enviar (Botão verde com aviãozinho) no preview
            send_btn = self.utilities.find_element_clickable(By.XPATH, "//span[@data-icon='send']")
            send_btn.click()
            
            logger.info(f"Arquivo enviado: {arquivo_path}")
            time.sleep(3) # Tempo para garantir o envio antes de trocar de página

        except Exception as e:
            logger.error(f"Erro ao enviar arquivo {arquivo_path}: {e}")
