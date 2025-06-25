import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 🛠️ Substitua este caminho pelo local onde você salvou o ChromeDriver
chrome_driver_path = "C:\\Users\\Mayvon\\Desktop\\Desafio Suape\\Scrap empresas\\chromedriver.exe"

# 📌 Configurações para evitar detecção como bot
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 🧠 Anti-detecção via script: remove webdriver=true
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
})

# 🌐 URL alvo
url = "https://www.suape.pe.gov.br/pt/negocios/mapa-de-empresas"
driver.get(url)
time.sleep(random.uniform(3, 5))

# 💡 Simula scroll como usuário
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
time.sleep(random.uniform(1.5, 3))

# 📦 Lista para armazenar dados
empresas = []

# 🔍 Busca todos os blocos de empresas
blocos = driver.find_elements(By.CSS_SELECTOR, "div.empresa")

print(f"🔎 Total de empresas encontradas: {len(blocos)}\n")

for i, bloco in enumerate(blocos, 1):
    try:
        nome = bloco.find_element(By.CSS_SELECTOR, ".titulo-empresa h3").text.strip()
        parags = bloco.find_elements(By.CSS_SELECTOR, "p")

        atividade = polo = None
        for p in parags:
            if "Atividade:" in p.text:
                atividade = p.text.replace("Atividade: ", "").strip()
            if "Polo:" in p.text:
                polo = p.text.replace("Polo: ", "").strip()

        # Pega coordenadas
        botao_mapa = bloco.find_element(By.CSS_SELECTOR, "a.empresa-mapa")
        lat = botao_mapa.get_attribute("data-lat")
        lng = botao_mapa.get_attribute("data-long")

        print(f"{i:03d}. {nome} | {polo} | {lat}, {lng}")

        empresas.append({
            "Nome": nome,
            "Atividade": atividade,
            "Polo": polo,
            "Coordenadas": {
                "lat": lat,
                "lng": lng
            }
        })

        time.sleep(random.uniform(0.5, 1.5))  # Simula tempo de leitura

    except Exception as e:
        print(f"❌ Erro ao processar empresa {i}: {e}")

# 💾 Exporta para JSON
with open("empresas_suape.json", "w", encoding="utf-8") as f:
    json.dump(empresas, f, indent=2, ensure_ascii=False)

print("\n✅ Extração finalizada! Dados salvos em 'empresas_suape.json'.")

driver.quit()
