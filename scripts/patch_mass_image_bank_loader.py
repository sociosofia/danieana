#!/usr/bin/env python3
from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
html=path.read_text(encoding='utf-8')
MARKER='BANK_IMAGE_MIGRATED'
if MARKER in html:
    print('Mass image bank loader already present; nothing to do.')
    raise SystemExit(0)

old='const QUESTIONS=[...(window.BANK_SOCIOLOGIA||[]),...(window.BANK_FILOSOFIA||[]),...(window.BANK_HISTORIA||[]),...(window.BANK_GEOGRAFIA||[])];'
new='const QUESTIONS=[...(window.BANK_SOCIOLOGIA||[]),...(window.BANK_FILOSOFIA||[]),...(window.BANK_HISTORIA||[]),...(window.BANK_GEOGRAFIA||[]),...(window.BANK_IMAGE_MIGRATED||[])];'
if old not in html:
    raise SystemExit('Mass image loader patch aborted: QUESTIONS anchor not found.')
html=html.replace(old,new,1)

geo='await loadScript("banks/geografia.js");'
if geo not in html:
    raise SystemExit('Mass image loader patch aborted: startup bank anchor not found.')
html=html.replace(geo,geo+'\nawait loadScript("banks/image-migrated.js");',1)
path.write_text(html,encoding='utf-8')
print(f'Mass image bank loader injected into {path}.')
