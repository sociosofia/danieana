#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

STYLE_ID = "danieana-image-support-style"
if f'id="{STYLE_ID}"' in html:
    print("Image support already present; nothing to do.")
    raise SystemExit(0)

required_markers = ["function start", "function renderQ", "function choose", "const QUESTIONS"]
missing = [marker for marker in required_markers if marker not in html]
if missing:
    raise SystemExit("Image patch aborted: core markers not found: " + ", ".join(missing))

ui_injection = r'''
<style id="danieana-image-support-style">
#imagePrep{
  position:fixed;inset:0;z-index:100000;display:none;place-items:center;
  background:rgba(24,32,51,.58);backdrop-filter:blur(5px);padding:20px
}
#imagePrep.show{display:grid}
#imagePrepCard{
  width:min(420px,92vw);background:#fffdf8;color:#182033;border-radius:18px;
  padding:18px;box-shadow:0 18px 60px rgba(0,0,0,.22);text-align:center
}
#imagePrepCard strong{display:block;font-size:16px;margin-bottom:8px}
#imagePrepProgress{font-size:13px;color:#697184}
.question-media{display:none;margin:10px 0 14px;text-align:center}
.question-media.show{display:block}
.question-media-item{margin:9px 0}
.question-media img{
  display:block;width:auto;height:auto;max-width:min(100%,720px);max-height:56vh;
  object-fit:contain;margin:0 auto;border-radius:12px;border:1px solid rgba(24,32,51,.10);
  background:#fff;cursor:zoom-in
}
.question-media-hint{font-size:11px;color:#697184;margin-top:6px}
.question-media-error{
  border:1px dashed #ddb2b2;background:#fbeeee;color:#a73c3c;border-radius:12px;
  padding:10px;font-size:12px;text-align:left
}
#questionImageLightbox{
  position:fixed;inset:0;z-index:100001;display:none;align-items:center;justify-content:center;
  background:rgba(12,16,26,.94);padding:16px
}
#questionImageLightbox.show{display:flex}
#questionImageLightbox img{
  max-width:96vw;max-height:92vh;width:auto;height:auto;object-fit:contain;
  border-radius:10px;background:#fff;cursor:zoom-out
}
#questionImageClose{
  position:fixed;top:max(12px,env(safe-area-inset-top));right:14px;width:42px;height:42px;
  border:0;border-radius:999px;background:#fff;color:#182033;font-size:25px;line-height:1;
  display:grid;place-items:center;box-shadow:0 5px 20px rgba(0,0,0,.25);z-index:100002
}
@media(max-width:650px){
  .question-media img{max-width:100%;max-height:34vh}
  #questionImageLightbox{padding:8px}
  #questionImageLightbox img{max-width:98vw;max-height:90vh}
}
</style>

<div id="imagePrep" role="status" aria-live="polite" aria-busy="true">
  <div id="imagePrepCard">
    <strong>Baixando imagens das questões…</strong>
    <div id="imagePrepProgress">Preparando…</div>
  </div>
</div>

<div id="questionImageLightbox" role="dialog" aria-modal="true" aria-label="Imagem ampliada">
  <button id="questionImageClose" type="button" aria-label="Fechar imagem ampliada">×</button>
  <img id="questionImageLarge" alt="">
</div>
'''

logic_injection = r'''
const QUESTION_IMAGE_CACHE="ana-dani-question-images-v1";
let QUESTION_IMAGE_OBJECT_URLS=[];

const DANIEANA_IMAGE_ORIGINAL_START=start;
const DANIEANA_IMAGE_ORIGINAL_RENDERQ=renderQ;
const DANIEANA_IMAGE_ORIGINAL_CHOOSE=choose;

start=async function(...args){
  const ids=args[0]??null;
  const selected=DANIEANA_IMAGE_ORIGINAL_CHOOSE(ids);
  if(!selected?.length)return;
  try{
    await prepareQuestionImages(selected);
  }catch(err){
    console.error("Falha ao preparar imagens do simulado.",err);
    alert("Não consegui baixar todas as imagens deste simulado. Verifique sua conexão e tente novamente.");
    return;
  }
  choose=()=>selected;
  try{
    return await DANIEANA_IMAGE_ORIGINAL_START(...args);
  }finally{
    choose=DANIEANA_IMAGE_ORIGINAL_CHOOSE;
  }
};

renderQ=function(...args){
  const result=DANIEANA_IMAGE_ORIGINAL_RENDERQ(...args);
  const q=S.session?.questions?.[S.session.current];
  if(q)renderQuestionMedia(q);
  return result;
};

function normalizedQuestionImages(q){
  let raw=[];
  if(Array.isArray(q?.images)) raw=q.images;
  else if(Array.isArray(q?.__media?.images)) raw=q.__media.images;
  else if(Array.isArray(q?.media?.images)) raw=q.media.images;
  else if(q?.image) raw=[q.image];

  return raw.map((item,index)=>{
    if(typeof item==="string") return {url:item,context:"enunciado",alt:`Imagem da questão ${index+1}`};
    return {
      ...item,
      url:item?.url||item?.src||"",
      context:item?.context||"enunciado",
      alt:item?.alt||`Imagem da questão ${index+1}`
    };
  }).filter(item=>item.url);
}

function statementQuestionImages(q){
  return normalizedQuestionImages(q).filter(item=>{
    const c=String(item.context||"enunciado").toLowerCase();
    return ["enunciado","statement","support","suporte"].includes(c);
  });
}

async function cachedQuestionImageResponse(url){
  if(!("caches" in window)){
    const direct=await fetch(url,{cache:"no-store"});
    if(!direct.ok) throw new Error(`HTTP ${direct.status} ao baixar ${url}`);
    return direct;
  }
  const cache=await caches.open(QUESTION_IMAGE_CACHE);
  let response=await cache.match(url);
  if(response) return response;
  response=await fetch(url,{cache:"no-store"});
  if(!response.ok) throw new Error(`HTTP ${response.status} ao baixar ${url}`);
  await cache.put(url,response.clone());
  return response;
}

async function prepareQuestionImages(questions){
  const unique=new Map();
  for(const q of questions||[]){
    for(const item of normalizedQuestionImages(q)){
      if(!unique.has(item.url)) unique.set(item.url,item);
    }
  }
  const images=[...unique.values()];
  if(!images.length) return;

  const overlay=document.getElementById("imagePrep");
  const progress=document.getElementById("imagePrepProgress");
  overlay?.classList.add("show");

  try{
    let done=0;
    for(const item of images){
      await cachedQuestionImageResponse(item.url);
      done++;
      if(progress) progress.textContent=`${done} de ${images.length}`;
    }
  }finally{
    overlay?.classList.remove("show");
  }
}

function revokeQuestionImageObjectUrls(){
  QUESTION_IMAGE_OBJECT_URLS.forEach(url=>URL.revokeObjectURL(url));
  QUESTION_IMAGE_OBJECT_URLS=[];
}

function openQuestionImage(src,alt=""){
  const box=document.getElementById("questionImageLightbox");
  const img=document.getElementById("questionImageLarge");
  if(!box||!img)return;
  img.src=src;img.alt=alt;
  box.classList.add("show");
  document.body.style.overflow="hidden";
}

function closeQuestionImage(){
  const box=document.getElementById("questionImageLightbox");
  const img=document.getElementById("questionImageLarge");
  box?.classList.remove("show");
  if(img){img.removeAttribute("src");img.alt=""}
  document.body.style.overflow="";
}

async function renderQuestionMedia(q){
  closeQuestionImage();
  let host=document.getElementById("questionMedia");
  if(!host){
    host=document.createElement("div");
    host.id="questionMedia";
    host.className="question-media";
    const text=document.getElementById("text");
    text?.parentNode?.insertBefore(host,text);
  }

  revokeQuestionImageObjectUrls();
  const images=statementQuestionImages(q);
  host.dataset.questionId=String(q?.id||"");
  host.innerHTML="";
  host.classList.toggle("show",images.length>0);
  if(!images.length)return;

  for(const item of images){
    const wrap=document.createElement("div");
    wrap.className="question-media-item";
    const img=document.createElement("img");
    img.alt=item.alt||"Imagem da questão";
    img.loading="eager";
    img.decoding="async";
    img.tabIndex=0;
    img.setAttribute("role","button");
    img.setAttribute("aria-label",(item.alt||"Imagem da questão")+". Toque ou clique para ampliar.");
    const hint=document.createElement("div");
    hint.className="question-media-hint";
    hint.textContent="Toque ou clique para ampliar";
    wrap.append(img,hint);
    host.appendChild(wrap);

    try{
      const response=await cachedQuestionImageResponse(item.url);
      const blob=await response.blob();
      const objectUrl=URL.createObjectURL(blob);
      QUESTION_IMAGE_OBJECT_URLS.push(objectUrl);
      if(host.dataset.questionId!==String(q?.id||"")){
        URL.revokeObjectURL(objectUrl);
        QUESTION_IMAGE_OBJECT_URLS=QUESTION_IMAGE_OBJECT_URLS.filter(x=>x!==objectUrl);
        return;
      }
      img.src=objectUrl;
      const expand=()=>openQuestionImage(objectUrl,item.alt||"Imagem da questão");
      img.addEventListener("click",expand);
      img.addEventListener("keydown",ev=>{
        if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();expand()}
      });
    }catch(err){
      console.error("Não foi possível exibir imagem da questão.",err);
      wrap.innerHTML='<div class="question-media-error">Não foi possível carregar esta imagem. Verifique sua conexão e tente abrir o simulado novamente.</div>';
    }
  }
}

document.getElementById("questionImageClose")?.addEventListener("click",closeQuestionImage);
document.getElementById("questionImageLightbox")?.addEventListener("click",ev=>{
  if(ev.target.id==="questionImageLightbox"||ev.target.id==="questionImageLarge")closeQuestionImage();
});
document.addEventListener("keydown",ev=>{if(ev.key==="Escape")closeQuestionImage()});
'''

core_anchor = html.rfind("\nupdateModePanels();")
if core_anchor < 0:
    raise SystemExit("Image patch aborted: startHumanasApp closing anchor not found.")
html = html[:core_anchor] + "\n" + logic_injection + "\n" + html[core_anchor:]

if "</body>" not in html:
    raise SystemExit("Image patch aborted: closing body tag not found.")
html = html.replace("</body>", ui_injection + "\n</body>", 1)
path.write_text(html, encoding="utf-8")
print(f"Image support injected into {path}.")
