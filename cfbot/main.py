from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
import json
import os

class InstagramBot:
    def __init__(self, batch_size=100, min_delay=0.3, max_delay=0.8, pause_after=1000):
        self.batch_size = batch_size
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.pause_after = pause_after
        self.on_progress = None
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def init_driver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Adiciona argumentos para evitar erros de permissão
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-site-isolation-trials')
            
            # Configuração do User Agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Pega o diretório do perfil do Chrome atual
            chrome_profile = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data')
            options.add_argument(f'--user-data-dir={chrome_profile}')
            options.add_argument('--profile-directory=Default')
            
            self.driver = webdriver.Chrome(options=options)
            
            # Executa JavaScript para ocultar que é automatizado
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
            
            self.logger.info("Driver do Chrome inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar driver: {str(e)}")
            return False
            
    def random_delay(self):
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
        
    def check_login_status(self):
        try:
            self.driver.get('https://www.instagram.com/')
            time.sleep(2)
            
            # Verifica se tem botão de login
            login_button = self.driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"]')
            if login_button and "Entrar" in login_button[0].text:
                return False
                
            # Verifica se tem avatar
            avatar = self.driver.find_elements(By.CSS_SELECTOR, 'img[alt*="profile"]')
            if not avatar:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao verificar login: {str(e)}")
            return False
            
    def collect_followers(self):
        try:
            if not self.init_driver():
                raise Exception("Não foi possível inicializar o Chrome")
                
            self.logger.info("Iniciando coleta de seguidores")
            
            # Verifica login
            if not self.check_login_status():
                raise Exception("Usuário não está logado")
                
            # Vai para a página de seguidores
            self.driver.get('https://www.instagram.com/accounts/access_tool/accounts_following_you')
            time.sleep(2)
            
            followers = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Carrega mais seguidores
                view_more = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Ver mais')]")
                if not view_more:
                    break
                    
                view_more[0].click()
                time.sleep(1)
                
                # Verifica se chegou ao fim
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                # Atualiza progresso
                current_followers = self.driver.find_elements(By.CSS_SELECTOR, "._aacl._aaco._aacw._aacx._aad7._aade")
                followers = [f.text for f in current_followers]
                
                if self.on_progress:
                    self.on_progress(len(followers), len(followers))
                    
            return followers
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar seguidores: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                
    def add_to_close_friends(self, followers):
        try:
            if not self.init_driver():
                raise Exception("Não foi possível inicializar o Chrome")
                
            self.logger.info("Iniciando adição aos melhores amigos")
            
            # Verifica login
            if not self.check_login_status():
                raise Exception("Usuário não está logado")
                
            # Vai para a página de melhores amigos
            self.driver.get('https://www.instagram.com/accounts/settings/close_friends/')
            time.sleep(2)
            
            total = len(followers)
            processed = 0
            actions_since_pause = 0
            
            # Processa todos os seguidores
            for username in followers:
                # Procura usuário
                search = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Pesquisar"]')))
                search.clear()
                search.send_keys(username)
                
                self.random_delay()
                
                # Clica no checkbox
                try:
                    checkbox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="checkbox"]')))
                    if not checkbox.is_selected():
                        checkbox.click()
                except:
                    self.logger.warning(f"Não foi possível adicionar {username}")
                    
                processed += 1
                actions_since_pause += 1
                
                # Atualiza progresso
                if self.on_progress:
                    self.on_progress(processed, total)
                    
                # Verifica se precisa pausar
                if actions_since_pause >= self.pause_after:
                    pause_time = random.randint(60, 180)  # 1-3 minutos
                    time.sleep(pause_time)
                    actions_since_pause = 0
                    
                self.random_delay()
                
            # Salva alterações
            save_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Concluído')]")))
            save_button.click()
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar aos melhores amigos: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                
    def run(self):
        try:
            if not self.init_driver():
                raise Exception("Não foi possível inicializar o Chrome")
                
            self.logger.info("Bot iniciado")
            
            # Verifica login
            if not self.check_login_status():
                raise Exception("Usuário não está logado")
                
            # Coleta seguidores
            followers = self.collect_followers()
            
            # Adiciona aos melhores amigos
            self.add_to_close_friends(followers)
            
        except Exception as e:
            self.logger.error(f"Erro durante execução: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()
