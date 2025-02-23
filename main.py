from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import os
import configparser
import platform
import argparse
import logging

# Configura logging para debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver(headless=True, user_data_dir=None):
    """Inicializa o WebDriver do Chrome."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
    if not headless:
        chrome_options.add_argument("--window-size=1920,1080")
    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=TorrentProfile")
    
    try:
        return webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        logging.error(f"Erro ao iniciar ChromeDriver: {str(e)}. Certifique-se de que o ChromeDriver está no PATH.")
        raise

def needs_login(driver, url):
    """Verifica se a URL requer login."""
    try:
        driver.get(url)
        time.sleep(2)
        login_indicators = [
            "//input[@id='username']",
            "//input[@id='login']",
            "//input[@name='username']",
            "//input[@type='password']",
            "//input[@id='password']",
            "//form[contains(@action, 'login')]",
            "//h1[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(text(), 'Entrar')]"
        ]
        for xpath in login_indicators:
            if driver.find_elements(By.XPATH, xpath):
                logging.info(f"Detectada tela de login em {url} com {xpath}")
                return True
        logging.info(f"Não detectada tela de login em {url}")
        return False
    except (NoSuchElementException, WebDriverException) as e:
        logging.error(f"Erro ao verificar login em {url}: {str(e)}")
        return False

def perform_login(driver, tracker, url, user_data_dir):
    """Abre o navegador para login manual."""
    driver.quit()
    driver = setup_driver(headless=False, user_data_dir=user_data_dir)
    driver.get(url)
    print(f"Por favor, faça login manualmente no {tracker} em {url}")
    print("Certifique-se de marcar 'Lembrar-me' se disponível para salvar os cookies.")
    input("Pressione Enter após fazer login com sucesso...")
    return driver

def capture_screenshots(driver, url, username, tracker, user_data_dir, base_output_dir="screenshots", full=False, timeout=5):
    """Captura screenshots do perfil especificado."""
    try:
        print(f"Acessando perfil: {url}")
        
        if not os.path.exists(base_output_dir):
            os.makedirs(base_output_dir)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if full:
            # Apenas captura completa com --full
            driver.get(url)
            time.sleep(timeout)
            total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            driver.set_window_size(1920, total_height)
            
            full_output_file = os.path.join(base_output_dir, f"{timestamp}_{tracker}_{username}_full.png")
            driver.save_screenshot(full_output_file)
            print(f"Screenshot completo salvo em: {full_output_file}")
        else:
            # Apenas captura visível sem --full
            driver.get(url)
            time.sleep(timeout)
            driver.set_window_size(1920, 1080)
            
            visible_output_file = os.path.join(base_output_dir, f"{timestamp}_{tracker}_{username}_visible.png")
            driver.save_screenshot(visible_output_file)
            print(f"Screenshot visível salvo em: {visible_output_file}")
        
        return driver
    
    except WebDriverException as e:
        print(f"Erro ao processar {url}: {str(e)}")
        return driver

def process_trackers_config(config_file="trackers.conf", user_data_dir=None, base_output_dir="screenshots", full=False, trackers=None, timeout=5):
    """Processa os trackers do arquivo de configuração."""
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        print(f"Arquivo {config_file} não encontrado!")
        return
    
    config.read(config_file)
    
    if not user_data_dir:
        system = platform.system()
        if system == "Windows":
            user = os.getenv("USERNAME")
            base_path = os.path.join(os.getenv("USERPROFILE", "C:\\Users"), "")
        else:
            user = os.getenv("USER")
            base_path = os.path.expanduser("~")
        if not user:
            raise EnvironmentError("Não foi possível determinar o usuário do sistema (USER ou USERNAME).")
        user_data_dir = os.path.join(base_path, user, ".chrome_torrent_profile")
    
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        print(f"Criado diretório de perfil: {user_data_dir}")
    
    # Lê os trackers padrão da seção [TRACKERS]
    if "TRACKERS" not in config.sections():
        print("Erro: Seção [TRACKERS] não encontrada em 'trackers.conf'!")
        return
    default_trackers = config.get("TRACKERS", "default_trackers", fallback="").replace(" ", "").split(",")
    if not default_trackers or default_trackers == [""]:
        print("Nenhum tracker padrão definido em 'default_trackers'!")
        return
    
    # Filtra os trackers a processar: usa --tk se fornecido, senão usa default_trackers
    trackers_to_process = trackers if trackers else default_trackers
    trackers_to_process = [t for t in trackers_to_process if t in config.sections()]
    if not trackers_to_process:
        print(f"Nenhum tracker válido encontrado para processar: {trackers_to_process}")
        return
    
    for tracker in trackers_to_process:
        base_url = config[tracker]["base_url"]
        users = config[tracker]["users"].split(",")
        print(f"Processando {tracker}...")
        
        test_url = f"{base_url}{users[0].strip()}"
        driver = setup_driver(headless=True, user_data_dir=user_data_dir)
        
        try:
            if needs_login(driver, test_url):
                print(f"{tracker} requer login.")
                driver = perform_login(driver, tracker, test_url, user_data_dir)
            else:
                print(f"{tracker} não requer login, prosseguindo com capturas.")
            
            if not driver.capabilities.get("chrome", {}).get("headless", True):
                driver.quit()
                driver = setup_driver(headless=True, user_data_dir=user_data_dir)
            
            for user in users:
                user = user.strip()
                full_url = f"{base_url}{user}"
                driver = capture_screenshots(driver, full_url, user, tracker, user_data_dir, base_output_dir, full, timeout)
        
        except WebDriverException as e:
            print(f"Erro ao processar tracker {tracker}: {str(e)}")
        
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para capturar screenshots de perfis de trackers torrent.")
    parser.add_argument("--full", action="store_true", help="Captura apenas a página completa (headless).")
    parser.add_argument("--tk", nargs="+", help="Especifica trackers a processar (ex.: --tk CBR TL)")
    parser.add_argument("--timeout", type=int, default=5, help="Tempo de espera em segundos para carregamento")
    parser.add_argument("--output-dir", default="screenshots", help="Diretório para salvar os screenshots")
    args = parser.parse_args()
    
    process_trackers_config(
        full=args.full,
        trackers=args.tk,
        timeout=args.timeout,
        base_output_dir=args.output_dir
    )