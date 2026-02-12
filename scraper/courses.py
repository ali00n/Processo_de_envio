# scraper/courses.py
import os
import time
import logging
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from utilities import Utilities
import config

logger = logging.getLogger(__name__)

class CourseScraper:
    def __init__(self, browser_manager):
        """
        Classe responsável por navegar e extrair dados dos cursos.
        :param browser_manager: Instância de BrowserManager.
        """
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()
        self.download_dir = config.DOWNLOAD_DIR

    def dowload_arquivo(self):
        """Busca e baixa arquivos disponíveis na página atual."""
        downloads = self.browser.find_elements_with_wait(
            By.XPATH,
            '//tbody//a[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"download")]'
        )

        for download in downloads:
            # rolar até o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download)
            time.sleep(0.5)

            # clicar
            download.click()
            time.sleep(5)

        if os.path.exists(self.download_dir):
            arquivos = os.listdir(self.download_dir)
            print("Arquivos atuais na pasta:", arquivos)
        else:
            print("Pasta de download não existe:", self.download_dir)

        time.sleep(1)

    def atividade_extensionista(self):
        """Navega pelos cursos de extensão e baixa materiais."""
        print("Navegando para Material de Apoio...")
        atividades = [
            'Atividade extensionista I',
            'Ciência de Dados e Big Data',
            'DevOps',
            'Desenvolvimento Mobile',
            'DEVOPS - Desenvolvimento Operações'
        ]

        # entrar no embed uma vez
        embed = self.browser.find_element_with_wait(By.XPATH, "//embed[contains(@src,'avisos.php')]")
        self.driver.switch_to.frame(embed)
        time.sleep(1)

        for atividade in atividades:
            try:
                # clicar em Material de Apoio
                material_apoio = self.browser.find_element_with_wait(By.XPATH, "//h3[contains(text(), 'Novos Avisos')]")
                self.scroll_by(self.driver, 200)  # Rolar um pouco para garantir que o link esteja visível
                material_apoio.click()
                time.sleep(1)

                texto_material = self.browser.find_element_with_wait(By.XPATH, "//h3[contains(text(), 'Material de Apoio')]")
                self.driver.execute_script("arguments[0].scrollIntoView();", texto_material)

                # clicar na atividade atual
                atvd_extensionista = self.browser.find_element_with_wait(
                    By.XPATH, f"//a[contains(text(), '{atividade}')]"
                )
                atvd_extensionista.click()
                time.sleep(1)

                self.dowload_arquivo()

                # voltar para lista
                material_apoio = self.browser.find_element_with_wait(By.XPATH, "//a[contains(text(), 'Material Apoio')]")

                # rolar pro topo
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)

                # clicar
                material_apoio.click()
            except Exception as e:
                logger.error(f"Erro ao processar atividade {atividade}: {e}")
                # Logica de recuperação poderia ser adicionada aqui

        print("Finalizado download de materiais de apoio.")

    def ciencia_de_dados(self):
        """Navega especificamente para o curso de Ciência de Dados."""
        print("Navegando para Ciência de Dados...")

        # Nota: O switch_to.frame deve ser gerenciado com cuidado se já estiver dentro do frame
        # Assumindo que voltamos para o contexto default antes de chamar esta função se necessário,
        # MAS no código original ele entrava no frame de novo. 
        # Vou assumir que o contexto precisa ser resetado ou verificado.
        self.driver.switch_to.default_content() 
        
        embed = self.browser.find_element_with_wait(By.XPATH, "//embed[contains(@src,'avisos.php')]")
        self.driver.switch_to.frame(embed)
        time.sleep(1)

        # CLICAR EM CIÊNCIA DE DADOS
        ciencia_dados = self.browser.find_element_with_wait(By.XPATH, "//a[contains(text(), 'Ciência de Dados')]")
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].scrollIntoView();", ciencia_dados)
        ciencia_dados.click()
        time.sleep(1)

    def extracao(self):
        """Extrai links e disciplinas de uma tabela específica."""
        # Nota: XPATH fixo pode ser frágil. Mantendo original.
        tabela = self.browser.find_element_with_wait(By.XPATH, '//*[@id="yui_3_18_1_1_1757728896011_59"]', 20)
        texto_tabela = tabela.text
        print(texto_tabela)

        linhas_tabela = self.browser.find_elements_with_wait(By.TAG_NAME, 'ul', timeout=10, parent=tabela)

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
            tema = WebDriverWait(self.driver, config.WAIT_TIME).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.course-content"))
            ).text
            return tema
        except TimeoutException:
            logger.error("Não foi possível extrair o tema da aula.")
            return ""

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
