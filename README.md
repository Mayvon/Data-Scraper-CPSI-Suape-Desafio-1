# SUAPE 'Data Scraper' e 'Web Harvester'

> **Origem:** Desafio SUAPE – Inovação Aberta 2025
> **Escopo original:** **Desafio #1** – *Sistema de Evasão de Pessoas*
> **Script‑base:** `extracao.py`
> **Autor:** Mayvon Alves
> **Licença:** MIT

Este repositório nasceu como **parte específica da solução que apresentei para o Desafio SUAPE #1 na Chamada de Inovação Aberta via CPSI 2025**. No contexto da chamada pública, o **único objetivo** do script foi **contar quantas empresas existem dentro do Complexo Industrial Portuário de SUAPE** e gerar um arquivo GeoJSON com seus pontos. Esse inventário numérico subsidiou análises posteriores do desafio, mas **nenhuma lógica de evacuação ou roteamento** está aqui – só a **raspagem e georreferenciamento**.

Depois do programa, evoluí o código para servir como **ferramenta genérica de *scraping***: basta parametrizar seletores ou plugar outro *parser* para coletar dados tabulares de qualquer página que apresente blocos repetitivos de HTML.

---

## Índice

1. [Contexto do Desafio](#contexto-do-desafio)
2. [Visão Geral do Código](#visão-geral-do-código)
3. [Adaptando para Outros Sites](#adaptando-para-outros-sites)
4. [Dependências](#dependências)
5. [Como Executar](#como-executar)
6. [Estrutura de Saída](#estrutura-de-saída)
7. [Design Decisions](#design-decisions)
8. [Próximos Passos](#próximos-passos)
9. [Contribuindo](#contribuindo)
10. [Referências](#referências)

---

## Contexto do Desafio

O **Estudo Técnico Preliminar (ETP)** do Desafio #1 (em `docs/Desafio_1.pdf`) pedia, como primeira etapa, um *levamento fidedigno* das empresas instaladas no perímetro oficial do porto. Com esse número em mãos, a equipe de inovação poderia:

1. **Dimensionar a população potencialmente exposta** em cenários de risco;
2. **Planejar testes de campo representativos** com base no total de stakeholders;
3. **Definir custos** de futuras integrações (ex.: licenças por empresa).

> 🔍 **Importante:** O *crawler* não contém qualquer lógica de avaliação de risco ou evacuação. Ele **apenas** gera a lista de empresas e respectiva contagem.

---

## Visão Geral do Código

| Camada                                         | Descrição                         | Dependências                 |
| ---------------------------------------------- | --------------------------------- | ---------------------------- |
|  **Estratégia 1 – Selenium**                 | Renderiza páginas JS‑heavy.       | `selenium`, `chromedriver`   |
|  **Estratégia 2 – Requests + BeautifulSoup** | *Scraping* de HTML estático.      | `requests`, `beautifulsoup4` |
|  **Estratégia 3 – Offline**                  | Parseia um HTML salvo localmente. | Nenhuma                      |

O script percorre as estratégias **nesta ordem** e para na primeira que obtiver dados válidos, salvando um **GeoJSON** (EPSG:4326) com os pontos.

### Fluxo resumido

```
main()   →   estratégia (1|2|3)   →   _parse_empresas_from_soup()   →   GeoJSON
```

---

## Adaptando para Outros Sites

O projeto agora é **config‑driven**:

### 1. Defina seletores em JSON

Crie `site_config.json` com os seletores/atributos que descrevem cada campo:

```json
{
  "empresa_block": "div.card",        // bloco repetitivo
  "nome": ".card-title",             // seletor para o nome
  "atividade": ".card-atividade",     // seletor para a atividade
  "polo": ".tag-polo",               // seletor para o polo (opcional)
  "lat": "data-lat",                 // atributo ou seletor para latitude
  "lng": "data-lng"                  // atributo ou seletor para longitude
}
```

### 2. Execute com a configuração

```bash
CONFIG_FILE=site_config.json python extracao.py --url "https://meu-site.com/lista"
```

### 3. Precisa de algo mais complexo?

Implemente um *parser* em `parsers/meu_site.py` com a assinatura:

```python
def parse(html: str) -> list[dict]:
    ...  # devolva features GeoJSON
```

O script detecta o módulo automaticamente via `--parser meu_site`.

---

## Dependências

* Python ≥ 3.9
* `beautifulsoup4`
* `requests`
* `selenium` (opcional)

```bash
pip install -r requirements.txt
```

---

## Como Executar

```bash
# 1 – clone
git clone https://github.com/seu-usuario/suape-data-scraper.git
cd suape-data-scraper

# 2 – opções (exemplos)
export CONFIG_FILE="site_config.json"
export HTML_FALLBACK="backup.html"
export CHROMEDRIVER="/usr/bin/chromedriver"

# 3 – run!
python extracao.py --url "https://site-alvo.com"
```

| Variável        | Default                    | Descrição                    |
| --------------- | -------------------------- | ---------------------------- |
| `CONFIG_FILE`   | *(vazio)*                  | JSON com seletores/atributos |
| `HTML_FALLBACK` | `suape_mapa_empresas.html` | HTML offline                 |
| `CHROMEDRIVER`  | `chromedriver`             | WebDriver                    |
| `SELENIUM_PORT` | `9515`                     | Porta Selenium               |

---

## Estrutura de Saída

`*.geojson` no padrão `FeatureCollection`, contendo:

* `geometry` – Point (lon, lat)
* `properties.Nome`
* `properties.Atividade`
* `properties.Polo` (opcional)

Pronto para **QGIS**, **GeoPandas**, **Kepler.gl**, **Mapbox GL JS** etc.

---

## Design Decisions

1. **Portabilidade first** – roda até em Pyodide sem `ssl`.
2. **Fail‑safe** – três estratégias minimizam falhas.
3. **Config‑driven** – seletores externos ao código.
4. **GeoJSON** – formato aberto e versionável.

---

## Próximos Passos

* CLI oficial (`python -m scraper --help`).
* Saída em CSV e Parquet.
* GitHub Actions para rodar *scraping* agendado.
* Exemplo de dashboard Streamlit.

---

## Contribuindo

Pull Requests são bem‑vindos! Antes, abra uma *issue* contendo:

* URL alvo;
* Campos desejados;
* Especificidades do HTML.

---

## Referências

* **ETP – Desafio #1** (`docs/Desafio_1.pdf`).
* Site oficial do Complexo de SUAPE.
* Beautiful Soup Documentation.

---

> Feito para o Desafio SUAPE, Chamada de Inovação Aberta 2025 – e evoluído para qualquer pessoa que precise de um *scraper* plug‑and‑play.
