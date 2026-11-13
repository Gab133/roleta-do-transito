# Fontes do acervo

| Campo | Valor |
|---|---|
| Documento | Lei nº 9.503, de 23 de setembro de 1997: Código de Trânsito Brasileiro (CTB) |
| Instituição | Congresso Nacional; texto compilado pelo Centro de Documentação e Informação da Câmara dos Deputados |
| Versão | "Norma atualizada": texto com as alterações posteriores (inclui, por exemplo, a Lei nº 14.440/2022 nos limites de velocidade) |
| URL | https://www2.camara.leg.br/legin/fed/lei/1997/lei-9503-23-setembro-1997-372348-normaatualizada-pl.html |
| Arquivo local | `data/raw/ctb_lei_9503_1997_camara.html` |
| Data da coleta | 13/11/2026 |
| Licença | Texto de lei: não é protegido por direito autoral (Lei nº 9.610/1998, art. 8º, IV) |
| Tamanho | 341 artigos + Anexo I (definições); cerca de 277 mil caracteres de texto útil, bem acima do mínimo do guia (25 páginas) |
| Pedaços indexados | 920 (um por artigo; artigos longos divididos por parágrafo e, quando a lista é longa, por inciso) |

## Por que esta fonte

- **Autoridade:** é a própria lei, no site oficial da Câmara dos Deputados.
- **Relevância:** todas as perguntas do quiz (velocidade, cinto, álcool, pontos, pedestres)
  estão no CTB.
- **Atualidade:** a versão "norma atualizada" já traz as mudanças feitas por leis posteriores.

## O que foi tirado do texto

- **Notas de edição** como "(Redação dada pela Lei nº ...)": não são regras e atrapalhavam a
  busca.
- **Artigos vetados** (só "(VETADO)"): não têm conteúdo.
- **Anexo II** (sinalização): são desenhos de placas, sem texto que a busca possa usar.

## Limites e riscos

| Risco | Como foi tratado |
|---|---|
| O Planalto (planalto.gov.br) bloqueou o download automático | Foi usado o texto compilado da Câmara, que também é oficial |
| A lei muda | A data da coleta está registrada. Para atualizar, basta baixar a página de novo e rodar `python rag.py` |
| Resoluções do CONTRAN não estão no acervo | Regras que a lei deixa para o CONTRAN (ex.: modelos de cadeirinha, tolerância do bafômetro) não são respondidas em detalhe |
| Dados pessoais | O acervo é só a lei, que é pública. O jogo não pede nem guarda dados de ninguém |
| Valores de taxas do Detran e estatísticas de acidentes | Não estão no CTB. O juiz deve recusar (testes T07 e T08) |
