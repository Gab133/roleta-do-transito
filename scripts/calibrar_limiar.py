"""Escolhe o LIMIAR de similaridade com perguntas que NÃO estão na matriz de testes.

Mede a similaridade do melhor trecho para perguntas sobre trânsito (deveriam passar) e para
perguntas de outros assuntos (deveriam ser barradas). Salva em docs/evidencias/calibracao_limiar.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rag  # noqa: E402

DENTRO = [
    "Posso estacionar em cima da calçada?",
    "Quando devo usar o farol baixo durante o dia?",
    "O que é uma via de trânsito rápido?",
    "Ultrapassar pela direita é permitido?",
    "Moto pode levar criança pequena na garupa?",
    "Quem tem preferência numa rotatória?",
    "Pode dirigir com a carteira vencida?",
    "O que acontece se eu avançar o sinal vermelho?",
    "Quantos pontos dá uma infração leve?",
    "Ambulância com sirene ligada tem prioridade?",
]
FORA = [
    "Qual é a capital da Austrália?",
    "Como faço um currículo?",
    "Qual o melhor time de futebol do Brasil?",
    "Como cuidar de um cachorro filhote?",
    "Quanto é 15 vezes 8?",
    "Qual remédio tomar para dor de cabeça?",
    "Como funciona a fotossíntese?",
    "Quem escreveu Dom Casmurro?",
    "Como declarar imposto de renda?",
    "Qual a previsão do tempo para amanhã?",
]

juiz = rag.Juiz()
dentro = [(q, round(juiz.buscar(q, 1)[0]["score"], 3)) for q in DENTRO]
fora = [(q, round(juiz.buscar(q, 1)[0]["score"], 3)) for q in FORA]
menor_dentro, maior_fora = min(s for _, s in dentro), max(s for _, s in fora)
resultado = {
    "dentro_do_tema": dentro, "fora_do_tema": fora,
    "menor_dentro": menor_dentro, "maior_fora": maior_fora,
    "ponto_medio": round((menor_dentro + maior_fora) / 2, 3),
    "limiar_em_uso": rag.LIMIAR,
    "dentro_barradas_pelo_limiar": [q for q, s in dentro if s < rag.LIMIAR],
    "fora_que_passam_pelo_limiar": [q for q, s in fora if s >= rag.LIMIAR],
}
saida = Path(__file__).resolve().parent.parent / "docs" / "evidencias" / "calibracao_limiar.json"
saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(resultado, ensure_ascii=False, indent=1))
