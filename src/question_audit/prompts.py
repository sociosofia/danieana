from __future__ import annotations
import json

PASS_ROLES = [
    "Resolva diretamente pela teoria e pelo comando, sem usar porcentagens de acerto ou pistas externas.",
    "Resolva por eliminação: teste cada alternativa contra o enunciado e escolha apenas ao final.",
    "Atue como crítico: tente refutar a resposta mais intuitiva e procure ambiguidade, pegadinha ou alternativa mais precisa.",
]


def build_prompt(question: dict, discipline_cfg: dict, pass_index: int) -> str:
    doors = "\n".join(f"- {d['id']}: {d['label']} — {d['description']}" for d in discipline_cfg["doors"])
    subtopics = "\n".join(f"- {s}" for s in discipline_cfg["subtopics"])
    role = PASS_ROLES[pass_index % len(PASS_ROLES)]
    return f"""Você audita uma questão de {discipline_cfg['discipline']} para um simulador escolar.

PAPEL DESTA PASSAGEM:
{role}

REGRAS:
1. Resolva a questão de forma independente. Não suponha que outra passagem existe.
2. Retorne apenas uma alternativa se houver uma melhor resposta.
3. Se o item estiver truncado, ambíguo, depender de contexto ausente ou tiver mais de uma resposta plausível, registre flags.
4. Classifique de forma AMPLA para o aplicativo. {discipline_cfg['classification_rule']}
5. Não faça indexação curricular SESI fina.

PORTAS:
{doors}

SUBTEMAS POSSÍVEIS:
{subtopics}

QUESTÃO:
{json.dumps(question, ensure_ascii=False, indent=2)}
"""
