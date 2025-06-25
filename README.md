# Raspador de Dados SUAPE – 'Data Scraper & Web Harvester'

> **Projeto original:** Desafio SUAPE (Inovação Aberta 2025)


Este repositório nasceu como **parte específica da solução que apresentei para o Desafio SUAPE #1 na Chamada de Inovação Aberta via CPSI 2025**. No contexto da chamada pública, o **único objetivo** do script foi **contar quantas empresas existem dentro do Complexo Industrial Portuário de SUAPE** e gerar um arquivo GeoJSON com seus pontos. Esse inventário numérico subsidiou análises posteriores do desafio, mas **nenhuma lógica de evacuação ou roteamento** está aqui – só a **raspagem e georreferenciamento**.

Depois do programa, evoluí o código para servir como **ferramenta genérica de *scraping***: basta parametrizar seletores ou plugar outro *parser* para coletar dados tabulares de qualquer página que apresente blocos repetitivos de HTML.

---

Guia rápido para usar o extracao-v1.py
Objetivo: gerar um arquivo empresas_suape.geojson contendo o nome, a atividade, o polo e as coordenadas das empresas listadas na página
https://www.suape.pe.gov.br/pt/negocios/mapa-de-empresas.

1. Instalação (1 min)
bash
Copiar
Editar
pip install selenium beautifulsoup4 requests
Se você não tiver o ChromeDriver instalado, pule o Selenium (o script continua funcionando).

2. Como o script trabalha
Ordem	Estratégia	Quando funciona	O que você precisa fazer
1	Selenium	Browser + Internet	Ter o ChromeDriver no PATH.
2	Requests + BeautifulSoup	Internet, mas sem JavaScript	Nada extra.
3	HTML offline	Sem Internet	Salvar a página como suape_mapa_empresas.html na mesma pasta.

O script tenta a estratégia 1; se falhar, tenta a 2; se falhar, tenta a 3.

3. Passo a passo
Abra o terminal na pasta onde está extracao.py.

(Opcional) Se você não tem Internet no ambiente de execução:

Abra o site no seu navegador.

Salve a página (Ctrl+S) como suape_mapa_empresas.html.

Rode:

bash
Copiar
Editar
python extracao.py
Ao terminar, procure o arquivo empresas_suape.geojson na mesma pasta.
Esse arquivo já pode ser aberto no QGIS ou importar no Google Maps.

4. Principais dúvidas
Pergunta	Resposta curtinha
“Preciso mexer no código?”	Não. Execute como está.
“Deu erro de Selenium?”	O script cai automaticamente para o modo Requests ou offline. Ignore.
“O arquivo GeoJSON serve para quê?”	Para visualizar as empresas e suas localizações em qualquer software de mapas.
“Posso mudar o nome do arquivo salvo?”	Sim – altere a variável SAIDA_GEOJSON nas primeiras linhas do script.


---


