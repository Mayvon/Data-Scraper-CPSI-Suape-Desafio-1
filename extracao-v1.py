import json
import logging
import os
import random
import socket
import sys
import time
from contextlib import closing, suppress
from typing import Dict, List, Optional

"""extracao.py – multimodal e portátil
--------------------------------------
Três estratégias, em ordem de preferência:

1. **Selenium** (requer chromedriver + acesso à Web)
2. **Requests + BeautifulSoup** (acesso à Web sem JS)
3. **Offline HTML** (parseia arquivo salvo localmente)

Quando o ambiente restringe acesso à Internet ‑ por exemplo, runtimes
*Pyodide*/WebAssembly usados por alguns notebooks online ‑ as duas primeiras
opções falham. Por isso adicionamos o modo 3: basta salvar o HTML da página em
`suape_mapa_empresas.html` (ou definir a variável de ambiente `HTML_FALLBACK`)
e o script extrairá as empresas desse arquivo.

Instalação mínima:
    pip install selenium beautifulsoup4 requests
"""

# ---------------------------------------------------------------------------
# 0. Patches para ambientes restritos (stub ssl + patch free_port) -----------
# ---------------------------------------------------------------------------
try:
    import ssl  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover – ssl ausente em Pyodide
    import types

    stub = types.ModuleType("ssl")
    stub.CERT_NONE = 0

    class _DummyCtx:  # pylint: disable=too-few-public-methods
        def __init__(self, *_a, **_kw):
            pass

    stub.create_default_context = lambda *_a, **_kw: _DummyCtx()  # type: ignore
    sys.modules["ssl"] = stub


# Evita socket.listen() (OSError 138 em emscripten)

def _safe_free_port() -> int:
    with suppress(Exception):
        import socket as _s
        with _s.socket(_s.AF_INET, _s.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]
    return 9515

with suppress(ModuleNotFoundError):
    import selenium.webdriver.common.utils as _sel_utils  # type: ignore

    _sel_utils.free_port = _safe_free_port  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# 1. Imports opcionais -------------------------------------------------------
# ---------------------------------------------------------------------------
from bs4 import BeautifulSoup  # type: ignore
import requests

CHROME_DRIVER_PATH = os.getenv("CHROMEDRIVER", "chromedriver")
SELENIUM_AVAILABLE = False
if os.path.exists(CHROME_DRIVER_PATH):
    try:
        from selenium import webdriver  # noqa: E402
        from selenium.webdriver.chrome.options import Options  # noqa: E402
        from selenium.webdriver.chrome.service import Service  # noqa: E402
        from selenium.webdriver.common.by import By  # noqa: E402
        from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
        from selenium.webdriver.support import expected_conditions as EC  # noqa: E402

        SELENIUM_AVAILABLE = True
    except ModuleNotFoundError:
        SELENIUM_AVAILABLE = False

# ---------------------------------------------------------------------------
# 2. Configurações globais ---------------------------------------------------
# ---------------------------------------------------------------------------
URL = "https://www.suape.pe.gov.br/pt/negocios/mapa-de-empresas"
SAIDA_GEOJSON = "empresas_suape.geojson"
OFFLINE_HTML = os.getenv("HTML_FALLBACK", "suape_mapa_empresas.html")
SELENIUM_PORT = int(os.getenv("SELENIUM_PORT", "9515"))
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
    )
}

# ---------------------------------------------------------------------------
# 3. Funções auxiliares ------------------------------------------------------
# ---------------------------------------------------------------------------

def _build_feature(nome: str, atividade: str, polo: str, lat: float, lng: float) -> Dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "properties": {"Nome": nome, "Atividade": atividade, "Polo": polo},
    }


def _parse_empresas_from_soup(soup: BeautifulSoup, origin: str) -> List[Dict]:
    blocos = soup.select("div.empresa")
    logging.info("%s empresas encontradas (%s).", len(blocos), origin)
    feats: List[Dict] = []
    for bloco in blocos:
        try:
            nome = bloco.select_one(".titulo-empresa h3").get_text(strip=True)
            atividade = polo = ""
            for p in bloco.select("p"):
                txt = p.get_text(strip=True)
                if txt.startswith("Atividade:"):
                    atividade = txt.replace("Atividade:", "", 1).strip()
                elif txt.startswith("Polo:"):
                    polo = txt.replace("Polo:", "", 1).strip()
            a = bloco.select_one("a.empresa-mapa")
            lat = float(a["data-lat"].replace(",", "."))  # type: ignore[index]
            lng = float(a["data-long"].replace(",", "."))  # type: ignore[index]
            feats.append(_build_feature(nome, atividade, polo, lat, lng))
        except Exception:
            logging.exception("Erro processando bloco (%s)", origin)
    return feats

# ---------------------------------------------------------------------------
# 4. Estratégia Selenium -----------------------------------------------------
# ---------------------------------------------------------------------------

def _scrape_selenium() -> Optional[List[Dict]]:
    if not SELENIUM_AVAILABLE:
        return None
    logging.info("Tentando Selenium…")
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"user-agent={HEADERS['User-Agent']}")
        service = Service(executable_path=CHROME_DRIVER_PATH, port=SELENIUM_PORT)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        with closing(driver):
            driver.get(URL)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.empresa"))
            )
            last_height = 0
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        return _parse_empresas_from_soup(soup, "Selenium")
    except Exception:
        logging.exception("Selenium falhou")
        return None

# ---------------------------------------------------------------------------
# 5. Estratégia Requests + BS4 ----------------------------------------------
# ---------------------------------------------------------------------------

def _scrape_requests() -> Optional[List[Dict]]:
    logging.info("Tentando requests + BS4…")
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return _parse_empresas_from_soup(soup, "BS4")
    except Exception:
        logging.exception("Requests falhou (sem acesso à Internet?)")
        return None

# ---------------------------------------------------------------------------
# 6. Estratégia Offline ------------------------------------------------------
# ---------------------------------------------------------------------------

def _scrape_offline() -> Optional[List[Dict]]:
    if not os.path.exists(OFFLINE_HTML):
        logging.error(
            "Modo offline: arquivo '%s' não encontrado. "
            "Baixe a página manualmente e salve com esse nome ou defina HTML_FALLBACK.",
            OFFLINE_HTML,
        )
        return None
    logging.info("Lendo HTML offline de %s", OFFLINE_HTML)
    with open(OFFLINE_HTML, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return _parse_empresas_from_soup(soup, "Offline")

# ---------------------------------------------------------------------------
# 7. Execução principal ------------------------------------------------------
# ---------------------------------------------------------------------------

def main() -> None:
    for strategy in (_scrape_selenium, _scrape_requests, _scrape_offline):
        features = strategy()
        if features:
            break
    else:
        logging.error("Nenhuma estratégia conseguiu extrair as empresas. Encerrando.")
        return

    geojson = {"type": "FeatureCollection", "features": features}
    with open(SAIDA_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    logging.info("Arquivo '%s' salvo com %d empresas.", SAIDA_GEOJSON, len(features))


if __name__ == "__main__":
    main()
