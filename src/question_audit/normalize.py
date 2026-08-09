from __future__ import annotations
import html
import re

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    value = TAG_RE.sub(" ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def contains_image(question: dict) -> bool:
    return bool(IMG_RE.search(question.get("statement_html") or "") or IMG_RE.search(question.get("support_html") or ""))


def question_payload(question: dict) -> dict:
    return {
        "id": str(question.get("id")),
        "institution": question.get("institution"),
        "year": question.get("year"),
        "exam_type": question.get("exam_type"),
        "phase": question.get("phase"),
        "difficulty": question.get("difficulty"),
        "statement": strip_html(question.get("statement_html")),
        "support": strip_html(question.get("support_html")),
        "alternatives": [
            {
                "letter": a.get("letter"),
                "text": strip_html(a.get("body_html")),
                "alternative_id": a.get("id"),
            }
            for a in (question.get("alternatives") or [])
        ],
    }
