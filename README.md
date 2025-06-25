# Raspador de Dados SUAPE – 'Data Scraper & Web Harvester'

> **Projeto original:** Desafio SUAPE (Inovação Aberta 2025)


Este repositório nasceu como **parte específica da solução que apresentei para o Desafio SUAPE #1 na Chamada de Inovação Aberta via CPSI 2025**. No contexto da chamada pública, o **único objetivo** do script foi **contar quantas empresas existem dentro do Complexo Industrial Portuário de SUAPE** e gerar um arquivo GeoJSON com seus pontos. Esse inventário numérico subsidiou análises posteriores do desafio, mas **nenhuma lógica de evacuação ou roteamento** está aqui – só a **raspagem e georreferenciamento**.

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


