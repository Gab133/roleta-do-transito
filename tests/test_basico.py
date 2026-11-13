"""Testes das partes que não dependem da IA. Rodar:  python -m pytest -q"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import rag  # noqa: E402


def test_limpeza_tira_notas_de_edicao():
    bruto = "Art. 165. Dirigir sob a influência de álcool:\n(Redação dada pela Lei nº 11.705, de 19/6/2008)\nInfração - gravíssima;"
    limpo = rag.limpar_texto(bruto)
    assert "Redação dada" not in limpo
    assert "Infração - gravíssima" in limpo


def test_limpeza_junta_linhas_quebradas_no_meio_da_frase():
    assert rag.limpar_texto("A velocidade máxima\npermitida para a via") == "A velocidade máxima permitida para a via"


def test_artigo_curto_vira_um_pedaco():
    assert rag.dividir_artigo("Art. 65. É obrigatório o uso do cinto.") == ["Art. 65. É obrigatório o uso do cinto."]


def test_artigo_longo_vira_um_pedaco_por_paragrafo_com_o_inicio_do_artigo():
    artigo = "Art. 148. Os exames de habilitação " + "x " * 560 + "\n§ 1º Curso.\n§ 2º Permissão para Dirigir, com validade de um ano."
    pedacos = rag.dividir_artigo(artigo)
    assert len(pedacos) == 3
    assert pedacos[2].startswith("Art. 148.") and "validade de um ano" in pedacos[2]


def test_separa_trecho_e_resposta():
    trecho, resposta = rag.separar("TRECHO: II - grave - cinco pontos;\nRESPOSTA: Cinco pontos (Art. 259).")
    assert trecho == "II - grave - cinco pontos;"
    assert resposta == "Cinco pontos (Art. 259)."


def test_saida_fora_do_formato_nao_se_perde():
    assert rag.separar("Cinco pontos (Art. 259).") == ("", "Cinco pontos (Art. 259).")


def test_perguntas_do_quiz_estao_bem_formadas():
    perguntas = json.loads((RAIZ / "perguntas.json").read_text(encoding="utf-8"))
    assert len(perguntas) == 20
    for p in perguntas:
        assert len(p["opcoes"]) == 4 and 0 <= p["correta"] < 4
        assert p["fonte"].startswith("Art. ")


def test_glossario_traduz_so_palavras_inteiras():
    assert rag.traduzir("Posso estacionar na calçada?") == "Posso estacionar na passeio (calçada)?"
    assert rag.traduzir("O motorista da moto") == "O motorista da motocicleta (moto)"   # "motorista" fica igual


def test_artigo_com_muitos_incisos_vira_um_pedaco_por_inciso():
    incisos = "\n".join(f"{n} - regra número {n} " + "y " * 60 for n in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])
    pedacos = rag.dividir_artigo("Art. 181. Estacionar o veículo:\n" + incisos)
    assert len(pedacos) == 10
    assert pedacos[7].startswith("Art. 181. Estacionar o veículo:\nVIII - ")
