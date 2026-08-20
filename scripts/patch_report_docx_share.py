#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

MARKER = "const DANIEANA_DOCX_REPORT_SHARE_V1=true;"
if MARKER in html:
    print("DOCX report sharing already present; nothing to do.")
    raise SystemExit(0)

old_button = 'Exportar relatório TXT para discussão'
if old_button in html:
    html = html.replace(old_button, 'Compartilhar relatório DOCX', 1)

start = html.find("function teacherReportText(){")
end = html.find('$("#wrong").onclick=()=>{', start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate teacher report export block.")

replacement = r'''const DANIEANA_DOCX_REPORT_SHARE_V1=true;
const DOCX_MIME="application/vnd.openxmlformats-officedocument.wordprocessingml.document";

function teacherReportSelection(){
  if(!last)return [];
  const chosen=new Set($$(".discCheck").filter(x=>x.checked).map(x=>x.dataset.id));
  return last.details.filter(d=>chosen.has(d.id));
}

function teacherReportParagraphs(){
  if(!last)return [];
  const ds=teacherReportSelection();
  const appTitle=document.querySelector("h1")?.textContent?.trim()||document.title||"Simulado de Ciências Humanas";
  const p=[];
  const add=(text,bold=false,kind="normal")=>p.push({text:String(text??""),bold,kind});
  add(appTitle,true,"title");
  add("RELATÓRIO PARA DISCUSSÃO COM O PROFESSOR",true,"subtitle");
  add("");
  add(`Modalidade: ${last.label||"Ciências Humanas"}`);
  add(`Data: ${last.date}`);
  add(`Resultado geral: ${last.correct}/${last.n} (${Math.round(last.correct/last.n*100)}%)`);
  add(`Tempo: ${fmt(last.secs)}`);
  add(`Questões selecionadas para discussão: ${ds.length}`);
  add("");
  ds.forEach(d=>{
    add(`QUESTÃO ${String(d.number).padStart(2,"0")}`,true,"heading");
    add(`Resultado: ${d.ok?"ACERTO":"ERRO"} | Como respondeu: ${confLabel(d.conf)} | Revisão: ${d.review?"SIM":"NÃO"}`);
    add(`Disciplina: ${discTitle(d.discipline)}`);
    add(`Tema: ${doorFor(d).title}${d.subtopic?` > ${d.subtopic}`:""}`);
    if(d.origin)add(`Origem: ${d.origin}`);
    add("");
    add("ENUNCIADO:",true);
    add(d.text||"");
    add("");
    add(`RESPOSTA DO ESTUDANTE: ${d.selectedLabel||"—"} — ${d.selectedText||"Não respondida"}`);
    add(`GABARITO: ${d.correctLabel||"—"} — ${d.correctText||""}`);
    if(d.solution){add("");add("COMENTÁRIO/RESOLUÇÃO:",true);add(d.solution)}
    add("");
  });
  return p;
}

function docxXmlEscape(value){
  return String(value??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\"/g,"&quot;").replace(/'/g,"&apos;");
}

function docxParagraphXml(item){
  const text=docxXmlEscape(item.text);
  const title=item.kind==="title";
  const subtitle=item.kind==="subtitle";
  const heading=item.kind==="heading";
  const size=title?32:(subtitle?24:(heading?24:22));
  const spacing=title?180:(heading?140:80);
  const align=(title||subtitle)?'<w:jc w:val="center"/>':'';
  const keep=heading?'<w:keepNext/>':'';
  const bold=item.bold?'<w:b/>':'';
  return `<w:p><w:pPr>${align}${keep}<w:spacing w:after="${spacing}"/></w:pPr><w:r><w:rPr>${bold}<w:sz w:val="${size}"/><w:szCs w:val="${size}"/></w:rPr><w:t xml:space="preserve">${text}</w:t></w:r></w:p>`;
}

let DOCX_CRC_TABLE=null;
function docxCrc32(bytes){
  if(!DOCX_CRC_TABLE){
    DOCX_CRC_TABLE=new Uint32Array(256);
    for(let n=0;n<256;n++){
      let c=n;
      for(let k=0;k<8;k++)c=(c&1)?(0xEDB88320^(c>>>1)):(c>>>1);
      DOCX_CRC_TABLE[n]=c>>>0;
    }
  }
  let crc=0xFFFFFFFF;
  for(const b of bytes)crc=DOCX_CRC_TABLE[(crc^b)&0xFF]^(crc>>>8);
  return (crc^0xFFFFFFFF)>>>0;
}

function docxU16(v){const a=new Uint8Array(2);new DataView(a.buffer).setUint16(0,v,true);return a}
function docxU32(v){const a=new Uint8Array(4);new DataView(a.buffer).setUint32(0,v>>>0,true);return a}
function docxConcat(parts){
  const len=parts.reduce((n,p)=>n+p.length,0),out=new Uint8Array(len);let o=0;
  for(const p of parts){out.set(p,o);o+=p.length}
  return out;
}
function docxDosDateTime(date=new Date()){
  const year=Math.max(1980,date.getFullYear());
  const time=(date.getHours()<<11)|(date.getMinutes()<<5)|Math.floor(date.getSeconds()/2);
  const day=((year-1980)<<9)|((date.getMonth()+1)<<5)|date.getDate();
  return {time,day};
}

function docxStoreZip(entries){
  const enc=new TextEncoder(),locals=[],centrals=[];let offset=0;
  const {time,day}=docxDosDateTime();
  for(const entry of entries){
    const name=enc.encode(entry.name),data=typeof entry.data==="string"?enc.encode(entry.data):entry.data;
    const crc=docxCrc32(data),flags=0x0800;
    const local=docxConcat([
      docxU32(0x04034b50),docxU16(20),docxU16(flags),docxU16(0),docxU16(time),docxU16(day),
      docxU32(crc),docxU32(data.length),docxU32(data.length),docxU16(name.length),docxU16(0),name,data
    ]);
    locals.push(local);
    const central=docxConcat([
      docxU32(0x02014b50),docxU16(20),docxU16(20),docxU16(flags),docxU16(0),docxU16(time),docxU16(day),
      docxU32(crc),docxU32(data.length),docxU32(data.length),docxU16(name.length),docxU16(0),docxU16(0),
      docxU16(0),docxU16(0),docxU32(0),docxU32(offset),name
    ]);
    centrals.push(central);offset+=local.length;
  }
  const centralData=docxConcat(centrals);
  const end=docxConcat([
    docxU32(0x06054b50),docxU16(0),docxU16(0),docxU16(entries.length),docxU16(entries.length),
    docxU32(centralData.length),docxU32(offset),docxU16(0)
  ]);
  return docxConcat([...locals,centralData,end]);
}

function buildTeacherReportDocxBlob(){
  const body=teacherReportParagraphs().map(docxParagraphXml).join("");
  const documentXml=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>${body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>`;
  const contentTypes=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>`;
  const rels=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`;
  const zip=docxStoreZip([
    {name:"[Content_Types].xml",data:contentTypes},
    {name:"_rels/.rels",data:rels},
    {name:"word/document.xml",data:documentXml}
  ]);
  return new Blob([zip],{type:DOCX_MIME});
}

function downloadTeacherReportDocx(file){
  const url=URL.createObjectURL(file),a=document.createElement("a");
  a.href=url;a.download=file.name;document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
}

$("#exportTeacher").onclick=async()=>{
  if(!last)return;
  const chosen=$$(".discCheck").filter(x=>x.checked).length;
  if(!chosen){alert("Selecione pelo menos uma questão para discussão.");return}
  const filename=`relatorio_discussao_professor_${new Date().toISOString().slice(0,10)}.docx`;
  const blob=buildTeacherReportDocxBlob();
  const file=new File([blob],filename,{type:DOCX_MIME,lastModified:Date.now()});
  const canShareFiles=!!navigator.share&&(!navigator.canShare||navigator.canShare({files:[file]}));
  if(canShareFiles){
    try{
      await navigator.share({files:[file],title:"Relatório para discussão com o professor",text:"Relatório do simulado em formato DOCX."});
      return;
    }catch(err){
      if(err?.name==="AbortError")return;
      console.warn("Compartilhamento nativo indisponível; usando download como alternativa.",err);
    }
  }
  downloadTeacherReportDocx(file);
};

'''

html = html[:start] + replacement + html[end:]
path.write_text(html, encoding="utf-8")
print(f"DOCX report sharing injected into {path}.")
