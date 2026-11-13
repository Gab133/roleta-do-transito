# Relatório: Roleta do Trânsito

Equipe: Gabriel Braga, Evandro Eufrasio e Ana Luíza.

## 1. Problema e usuário

**Usuário:** estudantes e pessoas que vão tirar a carteira de motorista.

**Problema:** quem estuda para a prova de trânsito costuma decorar respostas de apostila sem
saber de onde elas vêm. Quem pergunta a um chatbot comum recebe respostas sem fonte, que podem
estar erradas ou desatualizadas.

**Decisão que o jogo apoia:** aprender as regras de trânsito conferindo cada resposta na lei,
com o artigo à vista.

**Por que RAG:** um quiz comum só diz "certo" ou "errado". Um chatbot sem documentos pode
inventar uma regra. Com RAG, o juiz **procura na lei**, responde **só com o que achou**,
**mostra o artigo** e diz **"não encontrei"** quando a lei não fala do assunto.

## 2. Base documental

Um documento oficial e extenso: o **Código de Trânsito Brasileiro** (Lei nº 9.503/1997), no
texto atualizado da Câmara dos Deputados. São 341 artigos e o Anexo I de definições, cerca de
277 mil caracteres de texto útil, bem acima do mínimo do guia (25 páginas). Detalhes, licença,
data e riscos em [FONTES.md](FONTES.md).

## 3. Arquitetura

```
 lei (HTML oficial)
      │  1. PREPARAR: tira notas de edição e artigos vetados;
      │     1 pedaço por artigo (artigo longo: 1 por parágrafo ou por inciso,
      │     sempre com o começo do artigo)
      ▼
 920 pedaços ──2. INDEXAR: bge-m3 → vetores → FAISS (cosseno)
                                   │
 pergunta ──bge-m3──► 3. BUSCAR os 4 pedaços mais parecidos
                                   │
                  similaridade < 0,45? ──sim──► "Não encontrei" (1ª barreira)
                                   │ não
                                   ▼
                  4. RESPONDER (gemma4:e4b): copia o TRECHO e depois a RESPOSTA com (Art. N)
                                   │
                  TRECHO = NENHUM? ──sim──► "Não encontrei" (2ª barreira)
                                   │ não
                                   ▼
                  resposta + trecho usado + os 4 trechos com o artigo e o link oficial
```

| Arquivo | Papel |
|---|---|
| `rag.py` | O juiz: preparar, indexar, buscar e responder |
| `app.py` | O jogo (Streamlit): roleta, perguntas, "Pergunte ao juiz" |
| `perguntas.json` | 20 perguntas, 4 por categoria, cada uma com o artigo que a comprova |

## 4. Parâmetros e decisões

| Parâmetro | Valor | Decisão |
|---|---|---|
| Pedaço (chunk) | 1 artigo; acima de 1.200 caracteres, 1 por parágrafo (§) | Na v1 (janelas de tamanho fixo), o Art. 148 ficava diluído. Testamos janelas de 1.200, 800 e 600 caracteres e nenhuma resolveu. A divisão por parágrafo resolveu (busca do quiz de 19/20 para 20/20). Na v4, artigos com uma lista longa no caput (como o Art. 181, das proibições de estacionar) passaram a ser divididos também por inciso (I, II, III…) |
| Glossário da busca | calçada → passeio, carro → automóvel, moto → motocicleta, carteira de motorista → CNH, bafômetro → teste de alcoolemia, cadeirinha → dispositivo de retenção | O jogador escreve "calçada"; a lei escreve "passeio". O glossário só acrescenta o termo da lei à pergunta **na busca**; a IA recebe a pergunta original |
| Sobreposição | 200 caracteres | Só quando um parágrafo sozinho passa de 1.200 caracteres |
| Metadados | número do artigo em cada pedaço | É o que o juiz cita e o que o jogador confere |
| Top-k | 4 | A busca acertou o artigo nas 20 perguntas do quiz com k = 4 |
| Filtro | Só o CTB; sem notas de edição, artigos vetados e Anexo II (desenhos de placas) | Acervo fechado e oficial; notas atrapalhavam a busca |
| Limiar de similaridade | 0,45 | Ver 4.1 |
| Embeddings | `bge-m3` | Bom em português, roda local |
| LLM do juiz | `gemma4:e4b`, temperatura 0,1, semente 42 | Na v2, o `qwen2.5:7b` leu o número errado (T01: 90 em vez de 100 km/h). O gemma fez 10/10 e 20/20 nas mesmas perguntas |
| Prompt | Copiar o TRECHO, depois responder | Na v1 ("responda só com os trechos; se não houver, diga X"), o modelo recusava perguntas fáceis. Copiar o trecho primeiro o obriga a procurar antes de decidir |

### 4.1 Calibração do limiar

O limiar foi escolhido com **20 perguntas que não fazem parte da matriz**, para não ajustar o
sistema à prova (`scripts/calibrar_limiar.py`, resultado em
`evidencias/calibracao_limiar.json`):

| Versão | Perguntas de trânsito | Perguntas de outros assuntos | Arquivo |
|---|---|---|---|
| v3 | 0,485 a 0,729 | 0,225 a 0,520 | `calibracao_limiar_v3.json` |
| v4 (final) | 0,522 a 0,729 | 0,219 a 0,520 | `calibracao_limiar.json` |

Na v3 as faixas se sobrepunham: "Como faço um currículo?" (0,520) parecia mais com a lei do que
"Quem tem preferência numa rotatória?" (0,485). Na v4 elas quase se tocam (0,520 e 0,522), mas
um limiar "no meio" ficaria sem folga. Nenhum limiar separa tudo. Escolhemos **0,45**, que
deixa passar todas as perguntas de trânsito, e deixamos a 2ª barreira (o TRECHO = NENHUM) cuidar
das duas perguntas de fora que passam. Com o juiz final (gemma4:e4b), as duas foram recusadas e a pergunta da rotatória foi respondida com o Art. 29 (`evidencias/barreira2_gemma.json`).

**Ressalva:** num teste com o modelo antigo (qwen), "Como faço um currículo?" foi respondida com
o Art. 315, que fala do currículo **escolar** de educação no trânsito. A palavra é a mesma e o
assunto é outro. É um limite da busca por similaridade (seção 7).

## 5. Testes

Detalhes em [MATRIZ_DE_TESTES.md](MATRIZ_DE_TESTES.md).

| Versão | Mudança | Matriz (meta ≥ 8/10) | Quiz: busca / citação |
|---|---|---|---|
| v1 | Primeira versão (janelas de tamanho fixo, prompt simples, qwen2.5:7b) | 7/10 | 19/20 / 18/20 |
| v2 | Divisão por parágrafo + prompt "copiar o trecho primeiro" | 7/10 (8/10 com o critério do T02 corrigido) | 20/20 / 19/20 |
| v3 | Juiz trocado para gemma4:e4b | 10/10 | 20/20 / 20/20 |
| **v4** | Divisão por inciso + glossário da busca (a pergunta da calçada passou a ser respondida) | **10/10** | **20/20 / 20/20** |

**Variação.** A v4 foi rodada só com a semente 42. A v3 foi rodada com 3 sementes diferentes (42, 1 e 7): **30/30** na matriz e
**60/60** no quiz. A redação muda; os fatos e os artigos citados, não.

## 6. Segurança, privacidade e ética

| Tema | Medida |
|---|---|
| Privacidade | Tudo roda no computador (Ollama + FAISS). O jogo não pede nem guarda dados pessoais; o placar fica só na sessão aberta |
| Controle das fontes | Acervo fechado: só o CTB oficial. O jogador não consegue adicionar documentos |
| Instrução maliciosa | Os trechos vão marcados como `<trecho>` e o prompt diz que trechos e pergunta são conteúdo, não ordens. Teste T10: o juiz não obedeceu |
| Evidência insuficiente | Duas barreiras (limiar e TRECHO = NENHUM) e uma mensagem padrão de recusa |
| Excesso de confiança | Cada resposta mostra o trecho usado e os 4 trechos com o artigo e o link oficial, para o jogador conferir. Aviso fixo: não substitui o Detran nem um advogado |
| Lei desatualizada | Data da coleta registrada em [FONTES.md](FONTES.md); para atualizar, baixar a página e rodar `python rag.py` |

## 7. Limites conhecidos

1. **Um só documento.** Regras que o CTB deixa para o CONTRAN (modelos de cadeirinha,
   tolerância do bafômetro, placas) não estão no acervo.
2. **Similaridade não é assunto.** Palavras iguais com sentidos diferentes ("currículo")
   podem passar pelo limiar. A 2ª barreira segurou nos testes, mas não é garantia.
3. **Respostas incompletas.** O T02 citou só a idade e não a altura (as duas condições da
   lei). O critério automático não detecta omissões; por isso há a revisão humana.
4. **Trecho mostrado errado.** No T01 da v4, a resposta está certa (100 km/h), mas o trecho
   copiado é a linha vizinha do Art. 61 (110 km/h, pista dupla). Copiar o trecho ajuda, mas não
   garante que a IA copiou a linha certa.
5. **Recusa pouco útil.** No T10, o juiz recusou em vez de explicar que qualquer quantidade
   de álcool é punida.
6. **Variação do modelo.** Com 3 sementes, o resultado foi o mesmo (30/30), mas a redação muda,
   e uma resposta pode ficar mais ou menos completa (T02). Três sementes não provam que nunca
   vai errar.
7. **Lentidão.** Cerca de 16 s por resposta, às vezes bem mais, numa GPU de 8 GB.
8. **Não é orientação jurídica.** O jogo ensina a lei; não analisa casos concretos.

## 8. IA mentora

O guia pede uma IA como mentora nas 5 etapas. A mentora é o `qwen2.5:7b`, um modelo diferente
do juiz, rodando pelo script `scripts/ia_mentora.py` com os arquivos reais do projeto. Prompts,
respostas e decisões estão em [DIARIO_IA_MENTORA.md](DIARIO_IA_MENTORA.md).

## 9. Uso de IA na construção do projeto

Além da IA mentora exigida pelo guia, a equipe usou um assistente de IA (Claude) para ajudar a
escrever o código e os documentos. A equipe deve declarar esse uso ao professor, conforme as
regras da disciplina, e ser capaz de explicar cada parte do projeto.

## 10. Contribuições

Todos os integrantes contribuíram com ideias e com as perguntas do jogo. Gabriel Braga
desenvolveu o projeto. Evandro Eufrasio e Ana Luíza fizeram as pesquisas e elaboraram as
respostas, além de partes do projeto.
