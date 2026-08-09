from __future__ import annotations
import json
import os
from openai import OpenAI

SCHEMA = {
    "type": "object",
    "properties": {
        "answer_letter": {"type":"string","enum":["A","B","C","D","E"]},
        "confidence": {"type":"number","minimum":0,"maximum":1},
        "door_id": {"type":"string"},
        "subtopic": {"type":"string"},
        "flags": {
            "type":"array",
            "items":{"type":"string","enum":[
                "ambiguous_question",
                "multiple_plausible_answers",
                "missing_context",
                "truncated_text",
                "depends_on_unseen_image",
                "possible_cancellation",
                "none"
            ]}
        },
        "brief_reason": {"type":"string"}
    },
    "required":["answer_letter","confidence","door_id","subtopic","flags","brief_reason"],
    "additionalProperties": False
}


def solve(prompt: str, model: str) -> dict:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.responses.create(
        model=model,
        reasoning={"effort":"low"},
        input=prompt,
        text={
            "format":{
                "type":"json_schema",
                "name":"question_audit",
                "strict":True,
                "schema":SCHEMA
            }
        }
    )
    data = json.loads(response.output_text)
    if data.get("flags") == ["none"]:
        data["flags"] = []
    return data
