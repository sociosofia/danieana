#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
VERSION = (sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GITHUB_SHA", "local"))[:12]

sw_path = ROOT / "sw.js"
html_path = ROOT / "index.html"
if not sw_path.exists() or not html_path.exists():
    raise SystemExit("Safe updater: index.html or sw.js not found")

sw = sw_path.read_text(encoding="utf-8")

# Normalize the cache declaration to one versioned app cache. The question-image
# cache is deliberately separate and is not touched by this updater.
if re.search(r'const CACHE_PREFIX="[^"]+";\s*const CACHE_NAME=CACHE_PREFIX\+"[^"]+";', sw):
    sw = re.sub(
        r'const CACHE_PREFIX="[^"]+";\s*const CACHE_NAME=CACHE_PREFIX\+"[^"]+";',
        f'const CACHE_PREFIX="ana-dani-humanas-";\nconst CACHE_NAME=CACHE_PREFIX+"{VERSION}";',
        sw,
        count=1,
    )
elif re.search(r'const CACHE_NAME="[^"]+";', sw):
    sw = re.sub(
        r'const CACHE_NAME="[^"]+";',
        f'const CACHE_PREFIX="ana-dani-humanas-";\nconst CACHE_NAME=CACHE_PREFIX+"{VERSION}";',
        sw,
        count=1,
    )
else:
    raise SystemExit("Safe updater: cache declaration not found in sw.js")

# Do not force a newly installed worker over an active simulation. The user
# explicitly promotes the waiting worker from the in-app update pill.
sw = sw.replace("  self.skipWaiting();\n", "").replace("self.skipWaiting();\n", "")

# Limit cleanup to this app's versioned caches instead of deleting unrelated
# Cache Storage entries on the same github.io origin.
cleanup_old = r'caches\.keys\(\)\.then\(keys=>Promise\.all\(keys\.filter\(k=>k!==CACHE_NAME\)\.map\(k=>caches\.delete\(k\)\)\)\)'
cleanup_new = 'caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX) && k!==CACHE_NAME).map(k=>caches.delete(k))))'
sw = re.sub(cleanup_old, cleanup_new, sw, count=1)

if "SKIP_WAITING" not in sw:
    marker = 'self.addEventListener("fetch",event=>{'
    if marker not in sw:
        raise SystemExit("Safe updater: fetch handler marker not found")
    handler = '''self.addEventListener("message",event=>{
  if(event.data?.type==="SKIP_WAITING") self.skipWaiting();
});

'''
    sw = sw.replace(marker, handler + marker, 1)

sw_path.write_text(sw, encoding="utf-8")

html = html_path.read_text(encoding="utf-8")
if 'id="danieana-update-script"' not in html:
    updater = r'''
<style id="danieana-update-style">
#danieanaUpdate{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:99999;display:none;align-items:center;gap:8px;max-width:calc(100vw - 24px);padding:8px 10px 8px 12px;border:1px solid rgba(24,32,51,.14);border-radius:999px;background:#fff;box-shadow:0 8px 28px rgba(24,32,51,.18);font:600 13px/1.2 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#182033}
#danieanaUpdate.show{display:flex}
#danieanaUpdate button{border:0;border-radius:999px;background:#182033;color:#fff;padding:7px 10px;font:700 12px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer}
</style>
<div id="danieanaUpdate" role="status" aria-live="polite"><span>✨ Tem novidade</span><button id="danieanaUpdateBtn" type="button">Atualizar</button></div>
<script id="danieana-update-script">
(()=>{
  if(!("serviceWorker" in navigator))return;
  const box=document.getElementById("danieanaUpdate");
  const btn=document.getElementById("danieanaUpdateBtn");
  let waiting=null;
  let reloading=false;
  const show=worker=>{if(!worker)return;waiting=worker;box?.classList.add("show")};
  const watch=reg=>{
    if(reg.waiting && navigator.serviceWorker.controller)show(reg.waiting);
    reg.addEventListener("updatefound",()=>{
      const worker=reg.installing;
      if(!worker)return;
      worker.addEventListener("statechange",()=>{
        if(worker.state==="installed" && navigator.serviceWorker.controller)show(worker);
      });
    });
  };
  navigator.serviceWorker.addEventListener("controllerchange",()=>{
    if(reloading)return;
    reloading=true;
    location.reload();
  });
  btn?.addEventListener("click",()=>{
    if(!waiting)return;
    btn.disabled=true;
    btn.textContent="Atualizando…";
    waiting.postMessage({type:"SKIP_WAITING"});
  });
  window.addEventListener("load",async()=>{
    try{
      const reg=(await navigator.serviceWorker.getRegistration()) || (await navigator.serviceWorker.register("./sw.js"));
      watch(reg);
      reg.update().catch(()=>{});
      setInterval(()=>reg.update().catch(()=>{}),60*60*1000);
    }catch(err){console.warn("Verificação de atualização indisponível.",err)}
  });
})();
</script>
'''
    if "</body>" not in html:
        raise SystemExit("Safe updater: closing body tag not found")
    html = html.replace("</body>", updater + "\n</body>", 1)
    html_path.write_text(html, encoding="utf-8")

print("Safe app update version:", VERSION)
