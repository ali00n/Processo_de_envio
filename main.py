import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import logging
import urllib.parse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MoodleScraper:
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        headless: se True, roda o Chrome sem interface gráfica.
        wait_time: tempo máximo (segundos) para WebDriverWait.
        """
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """Configura o ChromeDriver com opções básicas."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("ChromeDriver iniciado com sucesso.")

    def entrar_site(self):
        # Aqui entraremos no site
        self.driver.get('https://moodle.faat.edu.br/moodle/login/index.php')
        time.sleep(1)

    def login(self, username: str, password: str):
        print('Iniciando robo...')

        '''Aqui faremos o login'''
        self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(username)
        time.sleep(1)

        # Insere no input a senha
        self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
        time.sleep(1)

        self.driver.find_element(By.XPATH, '//*[@id="loginbtn"]').click()
        return

    def navegar_para_quadro_aulas(self):
        """
        TODO: implementar navegação até a página onde estão as aulas.
        """
        disciplinas = self.driver.find_elements(By.XPATH,
                                                "/html/body/div[1]/div/section/div/div/section/div/div[2]/div/table")
        # Aqui entra na aula DevOps
        for i in range(len(disciplinas)):
            # Clica no link
            disciplinas[i].click()

            # Aguarda a página carregar ou realizar alguma ação
            time.sleep(2)

            # Volta para a página anterior
            self.driver.back()

            # Aguarda o carregamento da página original
            time.sleep(2)

        # try:
        #     aula_devops = WebDriverWait(self.driver, 10).until(
        #         EC.element_to_be_clickable(
        #             (By.XPATH, '/html/body/div[1]/div/section/div/div/section/div/div[2]/div/table/tbody/tr[1]/td/a'))
        #     )
        #     aula_devops.click()
        #     time.sleep(1)
        # except TimeoutException as TE:
        #     print("Erro ao entrar na aula: ", TE)

        
    def extrair_aula_do_dia(self, dia: int | None = None) -> str:
        """
        TODO: implementar lógica para extrair aula/tema do dia no Moodle.
        dia: 0=segunda ... 6=domingo. Se None, usa hoje.
        """
        if dia is None:
            dia = datetime.datetime.today().weekday()
        logger.info(f"Extraindo aula do dia {dia} (0=segunda).")
        return ""  # substitua pelo texto extraído

    def parse_tema(self, raw_text: str) -> dict:
        """
        Transforma texto bruto em estrutura organizada.
        Exemplo de saída: {'disciplina': 'DevOps', 'tema': 'CI/CD'}
        """
        # Exemplo: parse simples — você pode melhorar depois
        if not raw_text:
            return {"disciplina": "Não encontrada", "tema": "N/A"}
        partes = raw_text.split("—")
        return {
            "disciplina": partes[0].strip() if len(partes) > 0 else None,
            "tema": partes[1].strip() if len(partes) > 1 else None
        }

    def formatar_mensagem(self, info: dict) -> str:
        """
        Monta mensagem final para envio no WhatsApp.
        """
        return f"Hoje temos aula de {info.get('disciplina')} — tema: {info.get('tema')}"

    def enviar_whatsapp_via_selenium(self, phone: str, mensagem: str):
        """
        Envia mensagem pelo WhatsApp Web (precisa estar logado no QR Code).
        """
        try:
            msg_encoded = urllib.parse.quote(mensagem)
            url = f"https://web.whatsapp.com/send?phone={'011971736134'}&text={msg_encoded}"

            self.driver.get(url)

            # Espera botão de enviar aparecer
            send_btn = WebDriverWait(self.driver, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar']"))
            )
            send_btn.click()

            logger.info(f"Mensagem enviada para {phone}: {mensagem}")

        except TimeoutException:
            logger.error("Não foi possível enviar a mensagem: botão de enviar não encontrado.")

    def close(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
            logger.info("ChromeDriver fechado.")

# < ------------- PRINCIPAIS ------------- > #
if __name__ == "__main__":
    scraper = MoodleScraper(headless=False)  # headless=False para ver o navegador

    scraper.entrar_site()  # abre o site do Moodle

    # Aqui insere os dados do ‘login’
    scraper.login("6324605", "05082000")

    # Aqui procura aula por aula
    scraper.navegar_para_quadro_aulas()

    scraper.close()