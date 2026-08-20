#!/usr/bin/env python3
from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
html=path.read_text(encoding='utf-8')
MARKER='danieana-option-image-support-v1'
if MARKER in html:
    print('Option image support already present; nothing to do.')
    raise SystemExit(0)
if 'const QUESTION_IMAGE_CACHE="ana-dani-question-images-v1";' not in html:
    raise SystemExit('Option image patch aborted: base image support not found.')

css=r'''
<style id="danieana-option-image-support-v1">
.option .option-content{display:block;flex:1;min-width:0}
.option .option-text{display:block}
.option-media{display:block;margin-top:8px;text-align:center}
.option-media-item{display:block;margin:7px 0}
.option-media img{
  display:block;width:auto;height:auto;max-width:min(100%,520px);max-height:38vh;
  object-fit:contain;margin:0 auto;border-radius:10px;border:1px solid rgba(24,32,51,.10);
  background:#fff;cursor:zoom-in
}
.option-media-hint{display:block;font-size:10px;color:#697184;margin-top:5px;font-weight:500}
.option-media-error{display:block;border:1px dashed #ddb2b2;background:#fbeeee;color:#a73c3c;border-radius:10px;padding:8px;font-size:11px;text-align:left}
@media(max-width:650px){.option-media img{max-width:100%;max-height:32vh}}
</style>
'''

logic=r'''
const DANIEANA_OPTION_IMAGE_ORIGINAL_RENDERQ=renderQ;
renderQ=function(...args){
  const result=DANIEANA_OPTION_IMAGE_ORIGINAL_RENDERQ(...args);
  const q=S.session?.questions?.[S.session.current];
  if(q)renderOptionMedia(q);
  return result;
};

function alternativeQuestionImages(q){
  return normalizedQuestionImages(q).filter(item=>/^alternativa[_ -]?[a-z0-9]+$/i.test(String(item.context||"")));
}

function optionImageLabel(context){
  const match=String(context||"").match(/^alternativa[_ -]?(.+)$/i);
  return match?String(match[1]).trim().toUpperCase():"";
}

async function renderOptionMedia(q){
  const images=alternativeQuestionImages(q);
  if(!images.length)return;
  const questionId=String(q?.id||"");
  const grouped=new Map();
  for(const item of images){
    const label=optionImageLabel(item.context);
    if(!label)continue;
    if(!grouped.has(label))grouped.set(label,[]);
    grouped.get(label).push(item);
  }

  for(let idx=0;idx<(q.sessionOptions||[]).length;idx++){
    const option=q.sessionOptions[idx];
    const label=String(option?.label||"").toUpperCase();
    const items=grouped.get(label)||[];
    if(!items.length)continue;
    const button=document.querySelector(`[data-o="${idx}"]`);
    if(!button)continue;
    button.dataset.mediaQuestionId=questionId;

    let content=button.querySelector(":scope > .option-content");
    if(!content){
      const textNode=button.children[1];
      content=document.createElement("span");
      content.className="option-content";
      if(textNode){
        textNode.classList.add("option-text");
        textNode.replaceWith(content);
        content.appendChild(textNode);
      }else{
        button.appendChild(content);
      }
    }
    const media=document.createElement("span");
    media.className="option-media";
    content.appendChild(media);

    for(const item of items){
      const wrap=document.createElement("span");
      wrap.className="option-media-item";
      const img=document.createElement("img");
      img.alt=item.alt||`Imagem da alternativa ${label}`;
      img.loading="eager";
      img.decoding="async";
      const hint=document.createElement("span");
      hint.className="option-media-hint";
      hint.textContent="Toque ou clique para ampliar";
      wrap.append(img,hint);
      media.appendChild(wrap);

      try{
        const response=await cachedQuestionImageResponse(item.url);
        const blob=await response.blob();
        const objectUrl=URL.createObjectURL(blob);
        QUESTION_IMAGE_OBJECT_URLS.push(objectUrl);
        const active=S.session?.questions?.[S.session.current];
        if(String(active?.id||"")!==questionId||!button.isConnected||button.dataset.mediaQuestionId!==questionId){
          URL.revokeObjectURL(objectUrl);
          QUESTION_IMAGE_OBJECT_URLS=QUESTION_IMAGE_OBJECT_URLS.filter(x=>x!==objectUrl);
          continue;
        }
        img.src=objectUrl;
        img.addEventListener("click",ev=>{
          ev.preventDefault();ev.stopPropagation();
          openQuestionImage(objectUrl,img.alt||`Imagem da alternativa ${label}`);
        });
      }catch(err){
        console.error("Não foi possível exibir imagem da alternativa.",err);
        wrap.innerHTML='<span class="option-media-error">Não foi possível carregar esta imagem.</span>';
      }
    }
  }
}
'''
anchor=html.rfind('\nupdateModePanels();')
if anchor<0: raise SystemExit('Option image patch aborted: app closing anchor not found.')
html=html[:anchor]+'\n'+logic+'\n'+html[anchor:]
if '</body>' not in html: raise SystemExit('Option image patch aborted: closing body not found.')
html=html.replace('</body>',css+'\n</body>',1)
path.write_text(html,encoding='utf-8')
print(f'Option image support injected into {path}.')
