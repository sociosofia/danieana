#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

src = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
dst = Path(sys.argv[2] if len(sys.argv) > 2 else "_site/heloesthe")

if not (src / "index.html").exists():
    raise SystemExit(f"source app missing: {src}")

if dst.exists():
    shutil.rmtree(dst)

dst.mkdir(parents=True, exist_ok=True)

for p in src.iterdir():
    if p.name == dst.name:
        continue
    target = dst / p.name
    if p.is_dir():
        shutil.copytree(p, target)
    else:
        shutil.copy2(p, target)

print(f"Staged HeloeSthe subsite at {dst}")
