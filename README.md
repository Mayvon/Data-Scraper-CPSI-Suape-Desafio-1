# Raspador de Dados SUAPE – 'Data Scraper & Web Harvester'

> **Projeto original:** Desafio SUAPE (Inovação Aberta 2025)
> **Arquivo principal:** `extracao.py`
> **Autor:** Mayvon Alves
> **Licença:** MIT

Este script surgiu para **contar quantas empresas existem no Complexo de SUAPE**. Depois, foi transformado numa pequena **ferramenta de raspagem (scraping) genérica**, que você pode usar em qualquer site que tenha uma lista repetitiva (cartões, tabelas, blocos etc.).

Se você nunca raspou dados antes, siga este passo‑a‑passo.

---

## 1. O que o script faz?

1. **Acessa** a página indicada (online ou salva em disco).
2. **Encontra** cada bloco de empresa (ou produto, notícia, evento…).
3. **Lê** as informações principais (nome, atividade, latitude, longitude).
4. **Salva** tudo num arquivo **GeoJSON** (`empresas_suape.geojson`). Esse formato funciona em QGIS, GeoPandas, Google Maps, etc.

---

## 2. Instalação Rápida

```bash
# 1) Instale Python 3.9+ se ainda não tiver.
# 2) Baixe o projeto
git clone https://github.com/seu-usuario/suape-data-scraper.git
cd suape-data-scraper

# 3) Instale as bibliotecas necessárias
pip install -r requirements.txt  # leva menos de 1 minuto
```

> **Dica:** Se não for usar Selenium, você pode remover essa linha do `requirements.txt` para instalar menos coisas.

---

## 3. Primeiro teste (sem alterar nada)

```bash
python extracao.py  # usa o endereço padrão de SUAPE
```

Depois de alguns segundos você verá algo como:

```
[INFO] 83 empresas encontradas
[INFO] Arquivo 'empresas_suape.geojson' salvo
```

Pronto! O arquivo aparece na mesma pasta.

---

## 4. Usar em QUALQUER outro site

O script precisa de um **arquivo de configuração** dizendo onde estão os dados na página. Exemplo bem curto:

**site\_config.json**

```json
{
  "empresa_block": "div.card",
  "nome": ".card-title",
  "atividade": ".card-atividade",
  "lat": "data-lat",
  "lng": "data-lng"
}
```

* `empresa_block` → o CSS do bloco que se repete.
* `nome`, `atividade` → onde pegar texto.
* `lat`, `lng` → atributo ou seletor com as coordenadas.
* Campos que não existir (ex.: `polo`) podem ser omitidos.

### Executando

```bash
CONFIG_FILE=site_config.json \
python extracao.py --url "https://meu-site.com/lista"
```

Em segundos você terá `meu-site.geojson` com os pontos.

### E se o site não mostrar latitude/longitude?

Você ainda pode usar o script, mas terá que converter endereços em coordenadas (chama‑se **geocodificação**). Isso não está incluído aqui, mas serviços como Nominatim ou Google Maps API fazem isso.

---

## 5. Funciona mesmo SEM internet

Alguns ambientes (por exemplo, notebooks online) bloqueiam acesso à web. Faça assim:

1. Abra a página no seu navegador.
2. Salve como **HTML Completo** (Ctrl+S) e renomeie para `pagina.html`.
3. Execute:

   ```bash
   HTML_FALLBACK=pagina.html python extracao.py
   ```

O script lê o arquivo local.

---

## 6. Opções úteis (variáveis de ambiente)

| Nome            | Serve para…                        | Padrão                     |
| --------------- | ---------------------------------- | -------------------------- |
| `CONFIG_FILE`   | JSON com seletores                 | *(vazio)*                  |
| `HTML_FALLBACK` | Caminho do HTML offline            | `suape_mapa_empresas.html` |
| `CHROMEDRIVER`  | Caminho do ChromeDriver (Selenium) | `chromedriver`             |
| `SELENIUM_PORT` | Porta onde o driver escuta         | `9515`                     |

Você define assim (Linux/Mac):

```bash
export CONFIG_FILE=site_config.json
```

No Windows (PowerShell):

```ps1
setx CONFIG_FILE site_config.json
```

---

## 7. Quero entender o código (resumido)

```text
main()                # ponto de entrada
 ├─ tenta Selenium    # se disponível
 ├─ tenta Requests    # se a página é simples
 └─ tenta Offline     # se não houver Internet
      ↳ _parse_empresas_from_soup()  # extrai campos e monta GeoJSON
```

Se uma estratégia falhar, ele tenta a próxima — por isso quase sempre funciona.

---

## 8. Próximos passos (ideias)

* Exportar também em **CSV**.
* Criar menu de linha de comando (`python -m scraper --help`).
* Rodar todo dia com **GitHub Actions** para pegar dados novos.
* Fazer um **dashboard** no Streamlit mostrando o mapa.

---

## 9. Dúvidas ou problemas?

Abra uma **issue** aqui no GitHub descrevendo:

* Link da página que quer raspar;
* O que tentou fazer;
* Mensagens de erro (se houver).

Fico feliz em ajudar! 😉

---

> Desenvolvido durante o Desafio SUAPE 2025 e simplificado para qualquer pessoa que queira raspar listas da web.
