# Diário de validação com a IA mentora

## Como foi feito

- **Mentora:** `qwen2.5:7b`, rodando no Ollama. É um modelo **diferente** do juiz
  (`gemma4:e4b`), para que a IA não avalie a si mesma.
- **Script:** `scripts/ia_mentora.py`. Cada prompt é montado com os **arquivos reais** do
  projeto (`FONTES.md`, `rag.py`, calibração, respostas da v3).
- **Evidência:** prompt e resposta completos de cada etapa em
  `docs/evidencias/mentora/etapa_N.json`.
- **Regra da equipe:** nenhuma sugestão foi aceita sem conferir na lei ou nos testes.
- **Momento:** a mentora revisou a **versão v3**. A v4 (divisão por inciso e glossário da busca) veio
  depois, de um teste da equipe no jogo, e não da mentora.

Legenda: ✅ adotada · 🟡 adotada em parte · ❌ rejeitada · ⚠️ erro da mentora

---

## Etapa 1: Problema

**Prompt (resumo):** descrição do jogo e do usuário. "Avalie se RAG faz sentido. Compare com
um quiz de respostas fixas e com um chatbot sem documentos. Diga quem é o usuário, que decisão
ele toma e quais os riscos." (completo em `etapa_1.json`)

| Resposta da IA | Decisão da equipe | Alteração | Evidência |
|---|---|---|---|
| RAG faz sentido: respostas baseadas em fonte oficial, melhor que quiz fixo e que chatbot sem documentos | ✅ Confirma a escolha | Nenhuma | Relatório, seção 1 |
| "RAG = Robô de Assistência de Geração" | ⚠️ Errado: é *Retrieval-Augmented Generation* | Nenhuma | Guia, p. 3 |
| Risco: dependência de internet | ⚠️ Errado: tudo roda local, sem internet (só o download inicial dos modelos) | Nenhuma | `rag.py`, `OLLAMA = 127.0.0.1` |
| Risco: lei desatualizada | ✅ Já tratado | Nenhuma | `FONTES.md` (data da coleta) |
| Fazer verificação manual das respostas | ✅ Adotada | Revisão humana de cada resposta da matriz, nas 3 sementes | `MATRIZ_DE_TESTES.md`, seções 3 e 4 |

**Leitura da equipe:** confirmou a escolha de RAG, mas com dois erros de fato. Por isso cada
afirmação foi conferida.

## Etapa 2: Base

**Prompt (resumo):** problema + o `FONTES.md` inteiro. "Identifique lacunas, fontes frágeis,
desatualização e dados sensíveis. Diga se a base atende ao mínimo do guia."

| Resposta da IA | Decisão da equipe | Alteração | Evidência |
|---|---|---|---|
| "Faltam as categorias cinto de segurança e habilitação" | ⚠️ Errado: estão na lei e foram testadas (Art. 65 cinto; Arts. 140, 148, 259 e 261 habilitação). O quiz acerta o artigo nas 20 perguntas | Nenhuma | `resultados_v3.json`, parte B |
| Depender só do site da Câmara é frágil | 🟡 Procede em parte: a página pode mudar, mas a cópia usada está salva em `data/raw/` | Nenhuma | `data/raw/ctb_lei_9503_1997_camara.html` |
| Faltam regras detalhadas (cadeirinha, tolerância do bafômetro) | ✅ Correto: estão em resoluções do CONTRAN, fora do acervo | Registrado como limite | Relatório, seção 7, item 1 |
| A base supera o mínimo de 25 páginas | ✅ Confirma | Nenhuma | `FONTES.md` |

**Leitura da equipe:** a lacuna real (resoluções do CONTRAN) virou um limite documentado. A
lacuna inventada (cinto, habilitação) foi refutada com os testes.

## Etapa 3: Arquitetura

**Prompt (resumo):** problema + o código inteiro do `rag.py` + a calibração do limiar.
"Critique chunking, recuperação, top-k, limiar e prompt, em ordem de prioridade."

| Resposta da IA | Decisão da equipe | Alteração | Evidência |
|---|---|---|---|
| "Só o Art. 148 é dividido; os outros artigos longos não" | ⚠️ Errado: a função `dividir_artigo` divide **todo** artigo com mais de 1.200 caracteres | Nenhuma | `rag.py`, `dividir_artigo` |
| Subir o top-k para 6 | ❌ Rejeitada: com k = 4 a busca já acerta o artigo em 20/20 (nas 3 sementes). Mais trechos só aumentam o texto que a IA precisa ler | Nenhuma | `resultados_v3*.json`, parte B |
| Subir o limiar para 0,5 | ❌ Rejeitada: barraria "Quem tem preferência numa rotatória?" (0,485), que tem resposta na lei | Nenhuma | `calibracao_limiar_v3.json` |
| Tirar a exigência de copiar o trecho, para respostas "mais naturais" | ❌ Rejeitada: sem ela (v1), o juiz recusou 3 perguntas fáceis (7/10) | Nenhuma | `resultados_v1.json` |
| Usar embeddings "mais avançados, como BERT" | ❌ O `bge-m3` já é um modelo da família BERT (XLM-RoBERTa), multilíngue | Nenhuma | Documentação do bge-m3 |

**Leitura da equipe:** foi a etapa mais fraca. As sugestões contrariavam evidências que estavam
no próprio prompt (calibração) ou nos testes. Nenhuma foi adotada, e o motivo ficou registrado.

## Etapa 4: Respostas

**Prompt (resumo):** as 10 respostas da v3, cada uma com os trechos que o juiz recebeu. "Avalie
fidelidade, citação e alucinação, frase por frase."

| Resposta da IA | Decisão da equipe | Alteração | Evidência |
|---|---|---|---|
| Todas as 10 respostas são fiéis, sem alucinação | 🟡 Concorda no geral, mas a mentora **não viu** dois problemas que a revisão humana achou: T02 incompleta (falta a altura de 1,45 m) e T10 pouco útil (só recusou) | Registrados como limites | `MATRIZ_DE_TESTES.md`, seção 3 |
| "T02 cita os artigos 64 e 168" | ⚠️ Errado: a resposta cita só o Art. 64. O 168 estava entre os trechos, mas não foi citado | Nenhuma | `resultados_v3.json`, T02 |
| "Evitar lacunas como T07 a T10" | ⚠️ Entendeu errado: T07 a T10 **devem** ser recusados (perguntas sem resposta na lei ou maliciosas) | Nenhuma | Guia, p. 10 |

**Leitura da equipe:** uma IA de 7B não serve como revisora de fidelidade: deixou passar uma
omissão e inventou uma citação. Por isso a revisão de fidelidade do projeto é humana.

## Etapa 5: Riscos

**Prompt (resumo):** medidas de segurança atuais + o resultado real do T10. "Revise segurança,
privacidade, ética e instrução maliciosa. Considere excesso de confiança, lei desatualizada e
o risco de o jogo banalizar o tema."

| Resposta da IA | Decisão da equipe | Alteração | Evidência |
|---|---|---|---|
| O jogo pode banalizar o trânsito; incluir avisos sobre a seriedade | ✅ Adotada | Quando o jogador erra, aparece: "No jogo dá para errar e tentar de novo. No trânsito, essas regras protegem vidas." | `app.py` |
| Excesso de confiança: alertar o jogador | ✅ Já existia | Nenhuma: cada resposta mostra o trecho e o artigo, e há um aviso fixo | `app.py` |
| Migrar para a nuvem "para mais segurança" | ❌ Rejeitada: rodar local é o que garante que nada sai do computador | Nenhuma | Relatório, seção 6 |
| "Dados pessoais do jogador podem ser expostos" | ⚠️ O jogo não pede nem guarda dados pessoais | Nenhuma | `app.py` |
| Atualização automática da lei | 🟡 Procede, mas fica como trabalho futuro: hoje a atualização é manual (baixar a página e rodar `rag.py`) | Registrado | `FONTES.md` |

**Leitura da equipe:** a melhor contribuição de todas as etapas foi a de ética (não banalizar),
e ela foi adotada.

---

## Resumo

| Etapa | Sugestões úteis | Erros da mentora | Mudanças no projeto |
|---|---|---|---|
| 1 Problema | Verificação manual | 2 | Revisão humana em todas as rodadas |
| 2 Base | Lacuna do CONTRAN | 1 | Limite documentado |
| 3 Arquitetura | Nenhuma | 2 | Nenhuma (rejeições com evidência) |
| 4 Respostas | Confirmação geral | 2 | Nenhuma (a revisão humana já cobria) |
| 5 Riscos | Não banalizar o tema | 1 | Aviso no jogo |

**Conclusão:** a mentora foi útil como **lista de perguntas a conferir**, não como fonte de
verdade. Das sugestões, 2 viraram mudanças e as outras foram aceitas, já tratadas ou rejeitadas
com evidência. Dos 8 erros que ela cometeu, todos foram pegos porque a equipe conferiu cada
afirmação na lei e nos testes.
