# moodle_scraper.py
import time
import logging
import urllib.parse
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MoodleScraper:
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Classe para automação de login no Moodle, navegação em disciplinas
        e envio de mensagem via WhatsApp Web.

        :param headless: Se True, roda o Chrome sem interface gráfica.
        :param wait_time: Tempo máximo (segundos) para WebDriverWait.
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

    def find_element_with_wait(self, by, value, timeout=10, parent=None):
        if parent is None:
            parent = self.driver  # Usa o driver principal se nenhum elemento pai for passado
        return WebDriverWait(parent, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def find_elements_with_wait(self, by, value, timeout=10, parent=None):
        if parent is None:
            parent = self.driver  # Usa o driver principal se nenhum elemento pai for passado
        return WebDriverWait(parent, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    # -------------------- AÇÕES NO MOODLE -------------------- #
    def entrar_site(self):
        """Acessa a página inicial do Moodle."""
        self.driver.get("https://moodle.faat.edu.br/moodle/login/index.php")
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        print("Página do Moodle carregada.")

    def login(self, username: str, password: str):
        """Realiza login no Moodle."""
        print("Iniciando login no Moodle...")
        self.driver.find_element(By.ID, "username").send_keys(username)
        time.sleep(1)
        self.driver.find_element(By.ID, "password").send_keys(password)
        time.sleep(1)
        self.driver.find_element(By.ID, "loginbtn").click()
        time.sleep(1)
        return

        # card_body = self.find_element_with_wait(By.CLASS_NAME, 'card-body', 20)
        # links = card_body.find_elements(By.TAG_NAME, 'a')
        #
        # terceiro_link = links[2]
        # print(terceiro_link.text)
        # print(terceiro_link.get_attribute('href'))

    def aula_devops(self):

        dia_de_hoje = datetime.now()

        self.driver.execute_script("window.scrollTo(0, 1400);")
        time.sleep(1)

        # espera o elemento aparecer
        try:
            element = self.find_element_with_wait(
                By.XPATH, "//div[@id='category-course-list']//h4[contains(text(), 'DEVOPS')]"
            )

            # sobe pro link pai
            link = element.find_element(By.XPATH, "./ancestor::a")

            actions = ActionChains(self.driver)
            actions.move_to_element(link).click().perform()
            time.sleep(1)

            # Desce ate o final da tela
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            print("✅ Clique no curso DEVOPS realizado.")

        except Exception as e:
            print("❌ Erro ao clicar:", e)

        hoje = datetime.now().strftime("%d/%m/%Y")

        # encontra a UL
        ul_element = self.driver.find_element(By.XPATH, "//ul[@data-for='cmlist']")

        # encontra todos os LI dentro dela
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        div_li = ul_element.find_elements(By.TAG_NAME, "div")
        print(f"Quantidade de DIVs: {div_li.text}")

        if li_elements:
            # pega o último LI
            ultimo_li = li_elements[-1]
            print(ultimo_li.text)
            texto_li = ultimo_li.text.strip()

            print("Texto do último LI:", texto_li)

            # verifica se contém a data de hoje
            if hoje in texto_li:
                print("✅ O último LI contém a data de hoje!")
            else:
                print("❌ O último LI NÃO contém a data de hoje.")
        else:
            print("A UL não possui LIs.")

    def extracao(self):

        tabela = self.find_element_with_wait(By.XPATH, '//*[@id="yui_3_18_1_1_1757728896011_59"]', 20)
        texto_tabela = tabela.text
        print(texto_tabela)

        linhas_tabela = self.find_elements_with_wait(By.TAG_NAME, 'ul', timeout=10, parent=tabela)

        for linha in linhas_tabela:
            colunas = linha.find_elements(By.TAG_NAME, 'li')
            if len(colunas) >= 1:
                nome_disciplina = colunas[0].text
                link_disciplina = colunas[0].find_element(By.TAG_NAME, 'a').get_attribute('href')

                print(f"Disciplina: {nome_disciplina}")
                print(f"Link: {link_disciplina}")


    def extrair_aula_do_dia(self, dia: int | None = None) -> str:
        """
        Extrai o tema/aula do dia atual.
        :param dia: 0=segunda ... 6=domingo. Se None, usa hoje.
        :return: Texto bruto da aula/tema.
        """
        if dia is None:
            dia = datetime.datetime.today().weekday()
        logger.info(f"Extraindo aula do dia {dia} (0=segunda).")

        try:
            tema = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.course-content"))
            ).text
            return tema
        except TimeoutException:
            logger.error("Não foi possível extrair o tema da aula.")
            return ""

    # -------------------- PARSE E MENSAGEM -------------------- #
    def parse_tema(self, raw_text: str) -> dict:
        """
        Transforma texto bruto em estrutura organizada.
        Exemplo de saída: {'disciplina': 'DevOps', 'tema': 'CI/CD'}
        """
        if not raw_text:
            return {"disciplina": "Não encontrada", "tema": "N/A"}

        partes = raw_text.split("—")
        return {
            "disciplina": partes[0].strip() if len(partes) > 0 else None,
            "tema": partes[1].strip() if len(partes) > 1 else None,
        }

    def formatar_mensagem(self, info: dict) -> str:
        """Monta mensagem final para envio no WhatsApp."""
        return f"Hoje temos aula de {info.get('disciplina')} — tema: {info.get('tema')}"

    # -------------------- WHATSAPP -------------------- #
    def enviar_whatsapp_via_selenium(self, phone: str, mensagem: str):
        """
        Envia mensagem pelo WhatsApp Web (precisa estar logado no QR Code).
        :param phone: Número no formato DDI+DDD+número. Ex: 5511999999999
        :param mensagem: Texto da mensagem.
        """
        try:
            msg_encoded = urllib.parse.quote(mensagem)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={msg_encoded}"

            self.driver.get(url)

            send_btn = WebDriverWait(self.driver, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar']"))
            )
            send_btn.click()

            logger.info(f"Mensagem enviada para {phone}: {mensagem}")

        except TimeoutException:
            logger.error("Não foi possível enviar a mensagem: botão de enviar não encontrado.")

# -------------------- EXECUÇÃO PRINCIPAL -------------------- #
if __name__ == "__main__":
    scraper = MoodleScraper(headless=False)  # headless=True para rodar sem abrir navegador

    scraper.entrar_site()

    scraper.login("6324605", "05082000")

    scraper.aula_devops()

    scraper.extracao()

    raw = scraper.extrair_aula_do_dia()
    info = scraper.parse_tema(raw)
    msg = scraper.formatar_mensagem(info)

    scraper.enviar_whatsapp_via_selenium("5511971736134", msg)

