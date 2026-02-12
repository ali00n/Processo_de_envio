# main.py
import logging
from browser import BrowserManager
from auth import MoodleAuth
from scraper import CourseScraper
from whatsapp import WhatsAppSender

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    browser_manager = None
    try:
        # 1. Configurar Navegador
        browser_manager = BrowserManager()
        
        # 2. Login
        auth = MoodleAuth(browser_manager)
        auth.login()
        
        # 3. Scraping e Downloads
        scraper = CourseScraper(browser_manager)
        scraper.atividade_extensionista()
        scraper.ciencia_de_dados()
        scraper.extracao()
        
        # Exemplo de extração de tema do dia e envio de WhatsApp (comentado conforme original)
        tema = scraper.extrair_aula_do_dia()
        info_tema = scraper.parse_tema(tema)

        whatsapp = WhatsAppSender(browser_manager)
        msg = whatsapp.formatar_mensagem(info_tema)
        whatsapp.enviar_whatsapp_via_selenium("5511971736134", msg)

    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
    finally:
        # browser_manager.close() # Descomentar se desejar fechar automaticamente
        pass

if __name__ == "__main__":
    main()

