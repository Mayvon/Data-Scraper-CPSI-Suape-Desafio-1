# Raspador de Dados SUAPE – 'Data Scraper & Web Harvester'

> **Projeto original:** Desafio SUAPE (Inovação Aberta 2025)


Este repositório nasceu como **parte específica da solução que apresentei para o Desafio SUAPE #1 na Chamada de Inovação Aberta via CPSI 2025**. No contexto da chamada pública, este script foi desenvolvido para **contar quantas empresas existem dentro do Complexo Industrial Portuário de SUAPE** e gerar um arquivo GeoJSON com seus pontos georreferenciais. Esse inventário numérico subsidiou análises posteriores do desafio.

Depois do programa, evoluí o código para servir como **ferramenta genérica de *scraping***: basta parametrizar seletores ou plugar outro *parser* para coletar dados tabulares de qualquer página que apresente blocos repetitivos de HTML.

---
# Guia Rápido — `extracao.py`

> **Objetivo:** gerar `empresas_suape.geojson` com os pontos de todas as empresas listadas no  
> mapa oficial do Complexo Industrial Portuário de Suape.  
> O script tenta automagicamente **3 estratégias**, nesta ordem:  
> 1. **Selenium** (página real, JavaScript completo)  
> 2. **Requests + BeautifulSoup** (HTML direto, sem JS)  
> 3. **HTML offline** (arquivo salvo localmente)

---

## 1. Pré-requisitos

| Componente | Para quê? | Como instalar |
|------------|-----------|---------------|
| **Python ≥ 3.9** | executar o script | `sudo apt-get install python3` (Linux) |
| **pip** | gerenciar pacotes | já vem com Python 3.9+ |
| **Selenium** | estratégia 1 | `pip install selenium` |
| **Requests** | estratégia 2 | `pip install requests` |
| **BeautifulSoup 4** | estratégia 2 e 3 | `pip install beautifulsoup4` |
| **ChromeDriver** | estratégia 1 | baixar em <https://chromedriver.chromium.org/> e colocar no `PATH` ou definir `CHROMEDRIVER=/caminho/para/chromedriver` |

> *Sem ChromeDriver ou sem internet?*  
> Basta salvar a página como `suape_mapa_empresas.html` e o modo **offline** entra em ação automaticamente.

---

## 2. Instalação mínima

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install selenium requests beautifulsoup4
````

Se o `chromedriver` **não** estiver no `PATH`, exporte:

```bash
# Linux / macOS
export CHROMEDRIVER=/caminho/para/chromedriver
# Windows PowerShell
setx CHROMEDRIVER "C:\caminho\para\chromedriver.exe"
```

---

## 3. Execução

```bash
python extracao.py
```

* **Saída:** `empresas_suape.geojson` no mesmo diretório.
* **Logs:** mensagens informativas no terminal (`[INFO] ...`).

---

## 4. Variáveis de ambiente úteis

| Variável        | Exemplo                       | Efeito                                       |
| --------------- | ----------------------------- | -------------------------------------------- |
| `CHROMEDRIVER`  | `/usr/local/bin/chromedriver` | caminho do ChromeDriver                      |
| `SELENIUM_PORT` | `9515` (default)              | porta usada pelo Selenium                    |
| `HTML_FALLBACK` | `suape_mapa_empresas.html`    | nome do HTML offline                         |
| `HEADLESS`      | `1`                           | (já default) executa Chrome sem abrir janela |

---

## 5. Estrutura do GeoJSON gerado

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
    },
    …
  ]
}
```

Cada *feature* contém:

| Campo         | Descrição                        |
| ------------- | -------------------------------- |
| `Nome`        | Razão social da empresa          |
| `Atividade`   | Segmento de atuação              |
| `Polo`        | Polo dentro do complexo          |
| `coordinates` | `[longitude, latitude]` (WGS 84) |

---

## 6. Solução de problemas

| Sintoma                                    | Possível causa                              | Ação sugerida                               |
| ------------------------------------------ | ------------------------------------------- | ------------------------------------------- |
| `Selenium falhou`                          | ChromeDriver ausente ou versão incompatível | Verifique `CHROMEDRIVER` e versão do Chrome |
| `Requests falhou (sem acesso à Internet?)` | Sem internet / site bloqueando              | Use modo offline                            |
| `Nenhuma estratégia conseguiu…`            | Todos os métodos falharam                   | ⚠️ Verifique logs, dependências e variáveis |

---

## 7. Próximos passos

1. **Filtrar empresas** dentro da poligonal oficial?
   → Combine este GeoJSON com o perímetro `.geojson` do porto usando QGIS ou `geopandas`.

2. **Visualizar dados** rapidamente?

   ```bash
   pip install geopandas matplotlib
   python - <<'PY'
   import geopandas as gpd
   gdf = gpd.read_file('empresas_suape.geojson')
   gdf.plot(markersize=5)
   PY
   ```

3. **Integração em notebooks online (Pyodide)**

   * O script já inclui *patches* para SSL ausente e porta ocupada.
   * Garanta o upload do `HTML_FALLBACK` se a internet estiver bloqueada.

---

