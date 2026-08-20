#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/heloesthe")
TEXT_EXTS = {".html", ".js", ".css", ".json", ".webmanifest", ".txt", ".md"}

REPLACEMENTS = [
    ("Simulados da Ana e Dani", "HeloeSthe"),
    ("Simulados Ana e Dani", "HeloeSthe"),
    ("Ana e Dani", "Helo e Sthe"),
    ("Ana & Dani", "Helo & Sthe"),
    ("Ana/Dani", "Helo/Sthe"),
    ("para estudar ouvindo Anavitória 🎧", "Feito com afeto, para vocês. Estou na torcida!"),
    ("para estudar ouvindo Anavitória", "Feito com afeto, para vocês. Estou na torcida!"),
    ("ana-dani-question-images-v1", "heloesthe-question-images-v1"),
    ("danieana-image-support", "heloesthe-image-support"),
    ("danieanaUpdate", "heloestheUpdate"),
    ("danieana-update", "heloesthe-update"),
    ("ana-dani-humanas-", "heloesthe-humanas-"),
]


def replace_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def namespace_local_storage(html: str) -> str:
    marker = "heloesthe-local-storage-namespace"
    if marker in html:
        return html
    shim = r'''<script id="heloesthe-local-storage-namespace">
(()=>{
  const PREFIX="heloesthe:";
  const p=Storage.prototype;
  const get=p.getItem, set=p.setItem, rem=p.removeItem;
  p.getItem=function(k){return get.call(this,this===localStorage && !String(k).startsWith(PREFIX)?PREFIX+k:k)};
  p.setItem=function(k,v){return set.call(this,this===localStorage && !String(k).startsWith(PREFIX)?PREFIX+k:k,v)};
  p.removeItem=function(k){return rem.call(this,this===localStorage && !String(k).startsWith(PREFIX)?PREFIX+k:k)};
})();
</script>'''
    pos = html.lower().find("</head>")
    if pos < 0:
        raise SystemExit("HeloeSthe patch: </head> not found in index.html")
    return html[:pos] + shim + "\n" + html[pos:]


def patch_manifest(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    data["name"] = "HeloeSthe — Simulados de Humanas"
    data["short_name"] = "HeloeSthe"
    data["description"] = "Feito com afeto, para vocês. Estou na torcida!"
    data["start_url"] = "./"
    data["scope"] = "./"
    data["icons"] = [
        {"src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    index = ROOT / "index.html"
    if not index.exists():
        raise SystemExit(f"HeloeSthe patch: index.html not found under {ROOT}")

    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = replace_text(text)
        if path.name == "index.html":
            new = namespace_local_storage(new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1

    for name in ("manifest.json", "manifest.webmanifest"):
        p = ROOT / name
        if p.exists():
            patch_manifest(p)

    html = index.read_text(encoding="utf-8")
    required = [
        "HeloeSthe",
        "Feito com afeto, para vocês. Estou na torcida!",
        "heloesthe-local-storage-namespace",
        "Compartilhar relatório DOCX",
    ]
    missing = [x for x in required if x not in html]
    if missing:
        raise SystemExit(f"HeloeSthe patch validation failed; missing {missing}")
    if "Simulados da Ana e Dani" in html:
        raise SystemExit("HeloeSthe patch validation failed; Dani&Ana branding remains in index.html")

    sw = ROOT / "sw.js"
    if sw.exists():
        sw_text = sw.read_text(encoding="utf-8")
        if "ana-dani-humanas-" in sw_text or "ana-dani-question-images-v1" in sw_text:
            raise SystemExit("HeloeSthe patch validation failed; shared cache namespace remains in service worker")

    print(f"HeloeSthe subsite patch complete. Text files changed: {changed}")


if __name__ == "__main__":
    main()
