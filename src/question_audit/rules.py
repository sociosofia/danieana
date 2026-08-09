from __future__ import annotations
from collections import Counter
from .normalize import contains_image

SERIOUS_FLAGS = {
    "ambiguous_question",
    "multiple_plausible_answers",
    "missing_context",
    "truncated_text",
    "depends_on_unseen_image",
    "possible_cancellation",
}


def deterministic_answer(question: dict) -> dict | None:
    attempt = question.get("last_attempt") or {}
    if attempt.get("is_correct") is True and attempt.get("alternative_id"):
        for alt in question.get("alternatives") or []:
            if alt.get("id") == attempt["alternative_id"]:
                return {
                    "letter": alt.get("letter"),
                    "evidence": "KNOWN_CORRECT_ATTEMPT",
                    "confidence": 0.99,
                }
    return None


def hard_gate(question: dict, hold_images: bool = True) -> tuple[str | None, list[str]]:
    flags: list[str] = []
    if question.get("is_canceled"):
        flags.append("source_marked_cancelled")
        return "HOLD", flags
    if question.get("answer_type") != "MULTIPLE_CHOICE":
        flags.append("not_multiple_choice")
        return "HOLD", flags
    alts = question.get("alternatives") or []
    if len(alts) not in (4, 5):
        flags.append("unexpected_alternative_count")
        return "HOLD", flags
    if not question.get("statement_html"):
        flags.append("missing_statement")
        return "HOLD", flags
    if hold_images and contains_image(question):
        flags.append("depends_on_unseen_image")
        return "HOLD", flags
    return None, flags


def aggregate_passes(passes: list[dict], auto_min: float, review_min: float) -> dict:
    valid = [p for p in passes if p.get("answer_letter") in {"A","B","C","D","E"}]
    if not valid:
        return {"status":"HOLD","answer_letter":None,"confidence":0.0,"flags":["no_valid_model_answer"]}

    answers = Counter(p["answer_letter"] for p in valid)
    answer, votes = answers.most_common(1)[0]
    unanimous = votes == len(valid) and len(valid) >= 3
    majority = votes >= 2
    agreeing = [p for p in valid if p["answer_letter"] == answer]
    avg_conf = sum(float(p.get("confidence",0)) for p in agreeing) / max(1, len(agreeing))

    flags = sorted({f for p in valid for f in (p.get("flags") or [])})
    serious = bool(SERIOUS_FLAGS.intersection(flags))

    door_votes = Counter(p.get("door_id") for p in valid if p.get("door_id"))
    door = door_votes.most_common(1)[0][0] if door_votes else None
    sub_votes = Counter(p.get("subtopic") for p in valid if p.get("subtopic"))
    subtopic = sub_votes.most_common(1)[0][0] if sub_votes else None

    if unanimous and avg_conf >= auto_min and not serious:
        status = "AUTO_READY"
    elif majority and avg_conf >= review_min:
        status = "REVIEW"
    else:
        status = "HOLD"

    return {
        "status": status,
        "answer_letter": answer if majority else None,
        "confidence": round(avg_conf, 4),
        "answer_votes": dict(answers),
        "door_id": door,
        "subtopic": subtopic,
        "flags": flags,
        "passes": passes,
    }
