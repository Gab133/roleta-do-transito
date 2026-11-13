"""Roleta do Trânsito: quiz com um juiz que confere as respostas no Código de Trânsito.

Rodar:  streamlit run app.py
"""
import html
import math
import json
import random
from pathlib import Path

import requests
import streamlit as st

import rag

st.set_page_config(page_title="Roleta do Trânsito", page_icon="🚦", layout="centered")

PERGUNTAS = json.loads((Path(__file__).parent / "perguntas.json").read_text(encoding="utf-8"))
CATEGORIAS = list(dict.fromkeys(p["categoria"] for p in PERGUNTAS))
CORES = ["#E8553D", "#F2B33D", "#3BA676", "#3C7DD9", "#8E5BD0"]


@st.cache_resource(show_spinner="Abrindo o Código de Trânsito...")
def carregar_juiz() -> rag.Juiz:
    return rag.Juiz()


def desenhar_roleta(categoria_sorteada: str | None, giro: int) -> str:
    """Roleta em SVG. Quando há sorteio, ela gira e para com a categoria sorteada no ponteiro."""
    n, raio, centro = len(CATEGORIAS), 140, 150
    fatias = []
    for i, cat in enumerate(CATEGORIAS):
        a0, a1 = 2 * math.pi * i / n - math.pi / 2, 2 * math.pi * (i + 1) / n - math.pi / 2
        x0, y0 = centro + raio * math.cos(a0), centro + raio * math.sin(a0)
        x1, y1 = centro + raio * math.cos(a1), centro + raio * math.sin(a1)
        meio = (a0 + a1) / 2
        tx, ty = centro + raio * 0.62 * math.cos(meio), centro + raio * 0.62 * math.sin(meio)
        rot = math.degrees(meio)
        if 90 < rot < 270:                              # lado esquerdo: vira o texto para não ficar de ponta-cabeça
            rot -= 180
        cor = CORES[i % len(CORES)]
        cor_texto = "#3A2A00" if cor == "#F2B33D" else "#fff"   # texto escuro no amarelo, para dar contraste
        fatias.append(
            f'<path d="M{centro},{centro} L{x0:.1f},{y0:.1f} A{raio},{raio} 0 0,1 {x1:.1f},{y1:.1f} Z" '
            f'fill="{cor}" stroke="#fff" stroke-width="3"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" fill="{cor_texto}" font-size="11" font-weight="700" '
            f'text-anchor="middle" dominant-baseline="middle" font-family="Arial" '
            f'transform="rotate({rot:.1f} {tx:.1f} {ty:.1f})">{html.escape(cat)}</text>')
    angulo_final = 0
    if categoria_sorteada:
        i = CATEGORIAS.index(categoria_sorteada)
        meio_graus = 360 * (i + 0.5) / n               # a fatia i fica no topo girando -meio_graus
        angulo_final = 360 * 5 - meio_graus
    nome = f"giro{giro}"
    return f"""
<style>
@keyframes {nome} {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate({angulo_final}deg); }} }}
.roda-{giro} {{ transform-origin: 150px 150px; animation: {nome} 2.2s cubic-bezier(.15,.85,.25,1) forwards; }}
</style>
<div style="display:flex;justify-content:center">
<svg viewBox="0 0 300 310" width="300" height="310" role="img" aria-label="Roleta de categorias">
  <g class="roda-{giro}">{''.join(fatias)}</g>
  <circle cx="150" cy="150" r="24" fill="#1F2937" stroke="#fff" stroke-width="4"/>
  <text x="150" y="151" fill="#fff" font-size="20" text-anchor="middle" dominant-baseline="middle">🚦</text>
  <polygon points="150,22 138,0 162,0" fill="#1F2937"/>
</svg></div>"""


def mostrar_trechos(trechos: list[dict]) -> None:
    with st.expander("📖 Trechos da lei que o juiz consultou"):
        st.caption(f"Fonte: Lei nº 9.503/1997 (Código de Trânsito Brasileiro), texto atualizado da "
                   f"[Câmara dos Deputados]({rag.URL_FONTE}).")
        for t in trechos:
            st.markdown(f"**{t['fonte']}**: similaridade {t['score']:.2f}")
            st.markdown(f"<div style='font-size:0.85rem;color:#555;margin-bottom:0.8rem'>"
                        f"{html.escape(t['texto'][:900])}{'…' if len(t['texto']) > 900 else ''}</div>",
                        unsafe_allow_html=True)


# ------------------------------------------------------------------ estado do jogo
s = st.session_state
s.setdefault("pontos", 0)
s.setdefault("rodadas", 0)
s.setdefault("giro", 0)
s.setdefault("usadas", [])
s.setdefault("atual", None)        # índice da pergunta na tela
s.setdefault("escolha", None)      # alternativa escolhida
s.setdefault("parecer", None)      # resposta do juiz

st.title("🚦 Roleta do Trânsito")
st.caption("Gire, responda e veja o juiz conferir a resposta no Código de Trânsito Brasileiro.")

try:
    juiz = carregar_juiz()
except Exception as e:  # índice ausente
    st.error(f"Não foi possível abrir o índice: {e}. Rode `python rag.py` primeiro.")
    st.stop()

aba_jogo, aba_juiz = st.tabs(["🎡 Jogar", "⚖️ Pergunte ao juiz"])

with aba_jogo:
    c1, c2 = st.columns(2)
    c1.metric("Pontos", s.pontos)
    c2.metric("Rodadas", s.rodadas)

    categoria = PERGUNTAS[s.atual]["categoria"] if s.atual is not None else None
    st.markdown(desenhar_roleta(categoria, s.giro), unsafe_allow_html=True)

    if st.button("🎡 Girar a roleta", type="primary", use_container_width=True,
                 disabled=s.atual is not None and s.escolha is None):
        livres = [i for i in range(len(PERGUNTAS)) if i not in s.usadas] or list(range(len(PERGUNTAS)))
        if len(livres) == len(PERGUNTAS):
            s.usadas = []
        s.atual = random.choice(livres)
        s.usadas.append(s.atual)
        s.escolha, s.parecer = None, None
        s.giro += 1
        st.rerun()

    if s.atual is not None:
        p = PERGUNTAS[s.atual]
        st.subheader(f"{p['categoria']}")
        st.markdown(f"#### {p['pergunta']}")
        for i, opcao in enumerate(p["opcoes"]):
            if st.button(f"{'ABCD'[i]}) {opcao}", key=f"op{s.giro}-{i}", use_container_width=True,
                         disabled=s.escolha is not None):
                s.escolha = i
                s.rodadas += 1
                if i == p["correta"]:
                    s.pontos += 1
                st.rerun()

        if s.escolha is not None:
            correta = p["opcoes"][p["correta"]]
            if s.escolha == p["correta"]:
                st.success(f"✅ Acertou! Resposta: **{correta}**")
            else:
                st.error(f"❌ Errou. A resposta certa é: **{correta}**")
                # sugestão da IA mentora (etapa 5): o jogo não pode banalizar o tema
                st.caption("No jogo dá para errar e tentar de novo. No trânsito, essas regras protegem vidas.")
            if s.parecer is None:
                with st.spinner("O juiz está conferindo no Código de Trânsito..."):
                    try:
                        s.parecer = juiz.responder(
                            f"{p['pergunta']} Resposta: {correta}. Explique por que, citando o artigo.")
                    except requests.RequestException:
                        s.parecer = {"resposta": "O juiz está fora do ar: abra o Ollama e tente de novo.",
                                     "trechos": [], "status": "erro"}
            st.markdown("**⚖️ O juiz diz:**")
            st.info(s.parecer["resposta"])
            if s.parecer.get("trecho_usado"):
                st.caption(f"📌 Trecho da lei usado: “{s.parecer['trecho_usado']}”")
            if s.parecer["trechos"]:
                mostrar_trechos(s.parecer["trechos"])

with aba_juiz:
    st.write("Faça qualquer pergunta sobre trânsito. O juiz só responde o que está no Código de "
             "Trânsito e mostra o artigo. Se não estiver lá, ele avisa.")
    pergunta = st.text_input("Sua pergunta", placeholder="Posso estacionar em cima da calçada?")
    if st.button("Perguntar ao juiz", use_container_width=True):
        if not pergunta.strip():
            st.warning("Escreva uma pergunta primeiro.")
        else:
            with st.spinner("Procurando no Código de Trânsito..."):
                try:
                    r = juiz.responder(pergunta)
                except requests.RequestException:
                    r = {"resposta": "O juiz está fora do ar: abra o Ollama e tente de novo.",
                         "trechos": [], "status": "erro"}
            if r["status"] == "respondida":
                st.success(r["resposta"])
                if r.get("trecho_usado"):
                    st.caption(f"📌 Trecho da lei usado: “{r['trecho_usado']}”")
            else:
                st.warning(r["resposta"])
            if r["trechos"]:
                mostrar_trechos(r["trechos"])

st.divider()
st.caption("Jogo educativo. As respostas vêm do Código de Trânsito Brasileiro e não substituem "
           "orientação do Detran ou de um advogado. Tudo roda neste computador.")
