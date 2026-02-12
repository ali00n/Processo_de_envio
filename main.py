# main.py
import logging
from browser import BrowserManager
from auth import MoodleAuth
from scraper import CourseScraper
from whatsapp import WhatsAppSender
import os
import config

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
        scraper.limpar_downloads() # Limpar pasta antes de começar
        scraper.atividade_extensionista()
        scraper.ciencia_de_dados()
        scraper.extracao()
        
        # 4. Enviar Arquivos Baixados via WhatsApp
        whatsapp = WhatsAppSender(browser_manager)
        
        # Enviar aviso inicial
        # tema = scraper.extrair_aula_do_dia()
        # info_tema = scraper.parse_tema(tema)
        # msg = whatsapp.formatar_mensagem(info_tema)
        # whatsapp.enviar_whatsapp_via_selenium("5511971736134", msg)

        # Listar e enviar arquivos
        if os.path.exists(config.DOWNLOAD_DIR):
            arquivos = os.listdir(config.DOWNLOAD_DIR)
            phone_number = "5511971736134" # Configurar este número preferencialmente em config.py
            
            for arquivo in arquivos:
                caminho_completo = os.path.join(config.DOWNLOAD_DIR, arquivo)
                if os.path.isfile(caminho_completo):
                    logger.info(f"Enviando: {arquivo}")
                    whatsapp.enviar_arquivo(phone_number, caminho_completo)
        else:
            logger.warning("Pasta de downloads não encontrada.")

    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
    finally:
        if browser_manager:
            browser_manager.close() 
            pass
        print('robo finalizado !')

if __name__ == "__main__":
    main()
