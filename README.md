# Raspador de Dados para Desafio SUAPE 2025 – 'Data Scraper & Web Harvester'

> **Projeto original:** Desafio SUAPE (Inovação Aberta 2025)


Este repositório nasceu como **parte específica da solução que apresentei para o Desafio SUAPE #1 na Chamada de Inovação Aberta via CPSI 2025**. No contexto da chamada pública, este script foi desenvolvido para **contar quantas empresas existem dentro do Complexo Industrial Portuário de SUAPE** e gerar um arquivo GeoJSON com seus pontos georreferenciais. Esse inventário numérico subsidiou análises posteriores do desafio.

Depois do programa, evoluí o código para servir como **ferramenta genérica de *scraping***: basta parametrizar seletores ou plugar outro *parser* para coletar dados tabulares de qualquer página que apresente blocos repetitivos de HTML.

---

## Guia Rápido — `extracao.py`

> **Objetivo:** gerar `empresas_suape.geojson` com os pontos de todas as empresas listadas no  
> mapa oficial do Complexo Industrial Portuário de Suape.  
> O script tenta automagicamente **3 estratégias**, nesta ordem:  
> 1. **Selenium** (página real, JavaScript completo)  
> 2. **Requests + BeautifulSoup** (HTML direto, sem JS)  
> 3. **HTML offline** (arquivo salvo localmente)

---

### 1. Pré-requisitos

| Componente | Para quê? | Como instalar |
|------------|-----------|---------------|
| **Python ≥ 3.9** | executar o script | `sudo apt-get install python3` |
| **pip** | gerenciar pacotes | já vem com Python 3.9+ |
| **Selenium** | estratégia 1 | `pip install selenium` |
| **Requests** | estratégia 2 | `pip install requests` |
| **BeautifulSoup 4** | estratégia 2 e 3 | `pip install beautifulsoup4` |
| **ChromeDriver** | estratégia 1 | baixar em <https://chromedriver.chromium.org/> e pôr no `PATH` ou definir `CHROMEDRIVER=/caminho/para/chromedriver` |

> *Sem ChromeDriver ou sem internet?*  
> Salve a página como `suape_mapa_empresas.html` e o modo **offline** assume.

---

### 2. Instalação mínima

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install selenium requests beautifulsoup4
````

Se o `chromedriver` **não** estiver no `PATH`:

```bash
# Linux / macOS
export CHROMEDRIVER=/caminho/para/chromedriver
# Windows PowerShell
setx CHROMEDRIVER "C:\caminho\para\chromedriver.exe"
```

---

### 3. Execução

```bash
python extracao.py
```

* **Saída:** `empresas_suape.geojson` no mesmo diretório.
* **Logs:** mensagens `[INFO] …` no terminal.

---

### 4. Variáveis de ambiente úteis

| Variável        | Exemplo                       | Efeito                              |
| --------------- | ----------------------------- | ----------------------------------- |
| `CHROMEDRIVER`  | `/usr/local/bin/chromedriver` | caminho do ChromeDriver             |
| `SELENIUM_PORT` | `9515` (padrão)               | porta do Selenium                   |
| `HTML_FALLBACK` | `suape_mapa_empresas.html`    | nome do HTML offline                |
| `HEADLESS`      | `1`                           | executa Chrome sem UI (já é padrão) |

---

### 5. Estrutura do GeoJSON gerado

```jsonc
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [ -34.9201, -8.3562 ] },
      "properties": {
        "Nome": "Empresa X",
        "Atividade": "Logística",
        "Polo": "Polo Automotivo"
      }
    }
  ]
}
```

| Campo         | Descrição                        |
| ------------- | -------------------------------- |
| `Nome`        | Razão social                     |
| `Atividade`   | Segmento                         |
| `Polo`        | Polo industrial                  |
| `coordinates` | `[longitude, latitude]` (WGS 84) |

---

### 6. Solução de problemas

| Sintoma                         | Possível causa                              | Ação sugerida                     |
| ------------------------------- | ------------------------------------------- | --------------------------------- |
| `Selenium falhou`               | ChromeDriver ausente ou versão incompatível | Verifique `CHROMEDRIVER` e Chrome |
| `Requests falhou`               | Sem internet / site bloqueando              | Use modo offline                  |
| `Nenhuma estratégia conseguiu…` | Tudo falhou                                 | Leia os logs, cheque dependências |

---

### 7. Próximos passos

1. **Filtrar empresas pelo perímetro oficial** → use `geopandas` ou QGIS com o polígono do porto.

2. **Visualizar rapidamente**:

   ```bash
   pip install geopandas matplotlib
   python - <<'PY'
   import geopandas as gpd
   gdf = gpd.read_file('empresas_suape.geojson')
   gdf.plot(markersize=5)
   PY
   ```

3. **Rodar em notebooks WebAssembly (Pyodide)** → o script já traz *patches* para SSL e portas ocupadas; apenas faça upload do `HTML_FALLBACK` se necessário.

---

### 8. **Usando como Ferramenta Genérica de Scraping**

Quer adaptar para *qualquer* site que liste pontos no mapa ou cards em HTML?
Basta seguir estes **4 passos**:

| Passo                      | O que mudar                                               | Dica prática                                                       |
| -------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------ |
| **1. URL do alvo**         | `URL = "https://…"`                                       | pode virar argumento CLI (ex.: via `argparse`)                     |
| **2. Seletor dos blocos**  | `_parse_empresas_from_soup`: `soup.select("div.empresa")` | use o inspetor do navegador para achar a classe/ID dos itens       |
| **3. Extração dos campos** | Dentro do loop `for bloco in blocos:`                     | pegue `get_text(strip=True)` ou atributos `data-*` conforme o site |
| **4. Builder de saída**    | `_build_feature()`                                        | troque por CSV, XLSX, ou modifique as **properties** do GeoJSON    |

### Exemplo de parse genérico

```python
def _parse_items_generic(
    soup: BeautifulSoup,
    sel_item: str,
    sel_title: str,
    sel_lat: str,
    sel_lng: str,
) -> List[Dict]:
    feats = []
    for item in soup.select(sel_item):
        try:
            nome = item.select_one(sel_title).get_text(strip=True)
            lat = float(item[sel_lat])
            lng = float(item[sel_lng])
            feats.append(_build_feature(nome, "", "", lat, lng))
        except Exception:
            logging.exception("Erro processando item genérico")
    return feats
```

Chame assim:

```python
soup = BeautifulSoup(html, "html.parser")
features = _parse_items_generic(
    soup,
    sel_item="li.marker",          # bloco de cada ponto
    sel_title="h4",                # título dentro do bloco
    sel_lat="data-latitude",       # atributo com latitude
    sel_lng="data-longitude",      # atributo com longitude
)
```

#### Dicas extras

* **Sem mapa?** Fique só com Selenium + scroll infinito, trocando o seletor de rolagem se precisar.
* **Tabelas estáticas** não exigem Selenium: com `requests` + `pandas.read_html()` tudo sai em duas linhas.
* **Várias páginas**? Implemente um `for page in range(1, N):` e componha a URL.
* **CAPTCHA ou login**? Selenium + `driver.add_cookie()` ou bibliotecas de autenticação.
* **Outro formato de saída**? Substitua a parte “GeoJSON” por `csv.writer`, `pandas.DataFrame.to_excel()` etc.

---



