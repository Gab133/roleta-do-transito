# 🚦 Roleta do Trânsito

Quiz sobre trânsito com uma roleta de categorias e um **juiz** que confere cada resposta no
**Código de Trânsito Brasileiro** (Lei nº 9.503/1997). O juiz é um **RAG**: ele procura o
artigo certo na lei, responde citando o artigo e diz "não encontrei" quando a lei não fala do
assunto. Tudo roda no computador, com o Ollama.

## O que é RAG, em uma frase

Em vez de responder "de cabeça", a IA primeiro **procura nos documentos**, responde **só com
o que achou** e **mostra de onde tirou**. No jogo, os documentos são o Código de Trânsito.

## Como o jogo funciona

1. **🎡 Jogar:** gire a roleta, que sorteia uma categoria (Velocidade, Segurança, Álcool e
   celular, Habilitação, Pedestres e ciclistas). Escolha uma das 4 alternativas. O juiz confere
   a resposta na lei e mostra o artigo e o trecho usados.
2. **⚖️ Pergunte ao juiz:** escreva qualquer pergunta sobre trânsito. O juiz responde com o
   artigo, ou avisa que não encontrou no Código.

## Funcionando

| Roleta e pergunta | Juiz confere a resposta na lei |
|---|---|
| ![Roleta](docs/prints/02_roleta_sorteou_pergunta.png) | ![Juiz](docs/prints/03_resposta_conferida_pelo_juiz.png) |
| **Pergunta com resposta na lei (Art. 181)** | **Instrução maliciosa: o juiz não obedece** |
| ![Calçada](docs/prints/04_juiz_calcada_responde.png) | ![Maliciosa](docs/prints/07_juiz_instrucao_maliciosa.png) |

Resultados dos testes (versão final): matriz do guia **10/10**, quiz **20/20** (artigo achado e
citado). Todos os prints estão em [docs/prints](docs/prints).

## Documentos do trabalho

| Documento | Conteúdo |
|---|---|
| [Relatório](docs/RELATORIO.md) | Problema, base, arquitetura, parâmetros, testes, limites e decisões |
| [Matriz de testes](docs/MATRIZ_DE_TESTES.md) | As 10 perguntas do guia, critérios e histórico falha → ajuste |
| [Diário da IA mentora](docs/DIARIO_IA_MENTORA.md) | As 5 etapas: prompt, resposta, decisão, alteração, evidência |
| [Fontes](docs/FONTES.md) | De onde veio a lei, data da coleta e licença |
| [Apresentação](docs/Apresentacao_Roleta_do_Transito.pptx) | Slides |

Equipe: Gabriel Braga, Evandro Eufrasio e Ana Luíza, Levi Davi

## Como rodar

Requisitos: Python 3.11 ou mais novo e o [Ollama](https://ollama.com) instalado.

**1. Baixe os modelos (uma vez só):**

```bash
ollama pull bge-m3
```

```bash
ollama pull gemma4:e4b
```

```bash
ollama pull qwen2.5:7b
```

(o `gemma4:e4b` é o juiz; o `qwen2.5:7b` só é usado pela IA mentora)

**2. Crie o ambiente e instale as dependências:**

```bash
python -m venv .venv
```

```bash
.venv\Scripts\pip install -r requirements.txt
```

**3. Crie o índice da lei** (cerca de 1 minuto; só precisa refazer se mudar o código de preparação):

```bash
.venv\Scripts\python rag.py
```

**4. Abra o jogo:**

```bash
.venv\Scripts\streamlit run app.py
```

O jogo abre em http://localhost:8501. O Ollama precisa estar aberto.

## Como testar

| Comando | O que faz |
|---|---|
| `.venv\Scripts\python scripts\ia_mentora.py` | Roda as 5 etapas da IA mentora. Salva em `docs/evidencias/mentora/` |
| `.venv\Scripts\python -m pytest -q` | Testes das partes sem IA (limpeza, divisão em pedaços, formato) |
| `.venv\Scripts\python scripts\testar.py v4` | Matriz de 10 perguntas do guia + conferência das 20 perguntas do quiz. Salva em `docs/evidencias/resultados_v4.json`. Para outra semente da IA, rode antes `$env:RAG_SEED=7` |
| `.venv\Scripts\python scripts\calibrar_limiar.py` | Mede a similaridade de perguntas dentro e fora do tema para escolher o limiar |

## Arquivos

```
app.py                 o jogo (Streamlit): roleta, perguntas e as duas telas do juiz
rag.py                 o juiz (RAG): preparar a lei, indexar, buscar e responder
perguntas.json         as 20 perguntas do quiz, cada uma com o artigo que a comprova
data/raw/              texto oficial do Código de Trânsito (Câmara dos Deputados)
data/indice/           índice FAISS gerado pelo rag.py
scripts/testar.py      matriz de testes
scripts/calibrar_limiar.py   calibração do limiar
tests/                 testes unitários
docs/                  relatório, matriz de testes, diário da IA mentora, fontes, roteiro
```

## Parâmetros (todos no topo de `rag.py`)

| Parâmetro | Valor | Por quê |
|---|---|---|
| Pedaço (chunk) | 1 artigo; artigo com mais de 1.200 caracteres vira 1 pedaço por parágrafo (§) e, se tiver uma lista longa, 1 por inciso (I, II, III…), sempre com o começo do artigo | Cada pedaço fala de um assunto só, e a fonte fica sendo o artigo |
| Glossário da busca | calçada → passeio, carro → automóvel, moto → motocicleta, carteira de motorista → CNH, bafômetro → teste de alcoolemia, cadeirinha → dispositivo de retenção | O jogador fala "calçada"; a lei diz "passeio". Só a busca usa o glossário |
| Sobreposição | 200 caracteres (só quando um parágrafo passa de 1.200) | Não cortar uma regra no meio |
| Top-k | 4 pedaços | O suficiente para a resposta, sem confundir a IA |
| Limiar de similaridade | 0,45 | Calibrado com perguntas fora da matriz (ver relatório) |
| Embeddings | `bge-m3` | Bom em português, roda local |
| LLM do juiz | `gemma4:e4b`, temperatura 0,1, semente 42 (mude com `RAG_SEED`) | Acertou 10/10 onde o `qwen2.5:7b` fez 7/10 (ver relatório); temperatura baixa para ser previsível |
| IA mentora | `qwen2.5:7b` | Um modelo diferente do juiz, para não avaliar a si mesmo |
| Filtro | Só o Código de Trânsito; notas de edição e artigos vetados são removidos | Acervo fechado e oficial |

> Jogo educativo. Não substitui orientação do Detran nem de um advogado.
