#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://drivedepobre.com/api/questoes"
SAMPLES = {
    "sociologia": "4000001018",
    "filosofia": "4000007507",
    "historia": "4000000782",
    "geografia": "4000001265",
}
KNOWN_TOPIC_IDS = {
    "sociologia": "f7e83931-d18e-424e-b369-01a9d7dafceb",
    "filosofia": "76ccc99b-eb61-4a6a-bc9b-7a4395af4a41",
}

UA = "DaniAnaImageMigrationInventory/1.0 (+https://github.com/sociosofia/danieana)"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw.decode("utf-8")), r.status, dict(r.headers)


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            yield p, v
            yield from walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}[{i}]"
            yield p, v
            yield from walk(v, p)


def image_urls(obj):
    out = []
    for p, v in walk(obj):
        if isinstance(v, str) and re.search(r"https?://[^\s\"']+\.(?:png|jpe?g|webp|gif|svg)(?:\?[^\s\"']*)?", v, re.I):
            out.append({"path": p, "value": v[:500]})
    return out


def topic_candidates(obj):
    out = []
    for p, v in walk(obj):
        lp = p.lower()
        if "topic" in lp or "topico" in lp or "tópico" in lp or "subject" in lp or "discipl" in lp:
            if isinstance(v, (str, int, float, bool)) or v is None:
                out.append({"path": p, "value": v})
    return out


def compact_shape(obj, depth=0):
    if depth > 2:
        return type(obj).__name__
    if isinstance(obj, dict):
        return {k: compact_shape(v, depth+1) for k, v in list(obj.items())[:80]}
    if isinstance(obj, list):
        return [compact_shape(obj[0], depth+1)] if obj else []
    return type(obj).__name__


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "mass-migration-probe")
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"base": BASE, "known_topic_ids": KNOWN_TOPIC_IDS, "samples": {}}
    failures = []
    for discipline, qid in SAMPLES.items():
        url = f"{BASE}/q/{qid}"
        try:
            data, status, headers = fetch_json(url)
            (out_dir / f"{discipline}_{qid}_raw.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            report["samples"][discipline] = {
                "question_id": qid,
                "url": url,
                "http_status": status,
                "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
                "shape": compact_shape(data),
                "topic_candidates": topic_candidates(data),
                "image_references": image_urls(data),
            }
        except Exception as e:
            failures.append({"discipline": discipline, "question_id": qid, "error": repr(e)})
    report["failures"] = failures
    (out_dir / "probe_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
