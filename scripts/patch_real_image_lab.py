#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

MARKER = 'setTimeout(()=>{launchQuestionImageLab().catch(err=>console.error("Falha no laboratório de imagens.",err))},350);'
if 'const REAL_IMAGE_LAB_ID="SOC-4000245684";' in html:
    print("Real image lab already present; nothing to do.")
    raise SystemExit(0)
if MARKER not in html:
    raise SystemExit("Real image lab patch aborted: synthetic lab marker not found.")

real_lab = r'''

const REAL_IMAGE_LAB_ID="SOC-4000245684";
const REAL_IMAGE_LAB_QUESTION={
  id:REAL_IMAGE_LAB_ID,
  sourceQuestionId:"4000245684",
  discipline:"sociologia",
  text:`A fotografia é do antropólogo Bronislaw Malinowski (1884-1942) durante seu convívio com os habitantes das Ilhas Trobriand, na Melanésia, período em que pôde fazer uma descrição inédita da vivacidade de uma cultura. Fruto desse trabalho, Malinowski publicou, em 1922, a obra Argonautas do Pacífico ocidental. Um parágrafo clássico da introdução do livro dá o sabor de sua narrativa: “Imagine-se o leitor sozinho, rodeado apenas de seu equipamento, numa praia tropical próxima a uma aldeia nativa, vendo a lancha ou o barco que o trouxe afastar-se no mar e desaparecer de vista. Tendo encontrado um lugar para morar no alojamento de algum homem branco – negociante ou missionário – você nada tem a fazer a não ser iniciar imediatamente seu trabalho...” Nesse contexto, o antropólogo inaugura um método de pesquisa que, a partir de então, passou a ser amplamente utilizado. Trata-se do método`,
  support:"",
  images:[{
    url:"./media/q_4000245684.png",
    context:"enunciado",
    alt:"Bronislaw Malinowski durante trabalho de campo nas Ilhas Trobriand"
  }],
  options:[
    {label:"A",text:"missionário"},
    {label:"B",text:"positivista"},
    {label:"C",text:"etnocêntrico"},
    {label:"D",text:"etnográfico"}
  ],
  correct:3,
  gabarito:"D",
  category:"sociedade",
  subtopic:"Antropologia e etnografia",
  origin:"Simulado UERJ · 2022",
  institution:"Simulado UERJ",
  year:2022,
  difficulty_band:"Intermediária",
  solution:`O método etnográfico envolve observação participante e a descrição de uma cultura a partir do ponto de vista dos grupos estudados. Malinowski destacou a permanência prolongada do antropólogo em campo, o aprendizado da língua e a participação na vida cotidiana.`
};

async function launchRealQuestionImageLab(){
  const params=new URLSearchParams(location.search);
  if(params.get("realImageLab")!=="1")return;
  if(!QUESTIONS.some(q=>q.id===REAL_IMAGE_LAB_ID))QUESTIONS.unshift(REAL_IMAGE_LAB_QUESTION);
  localStorage.removeItem(K.active);
  S.study="area";S.discipline="sociologia";S.format="training";S.timer=false;S.count=1;S.fresh=false;
  await start([REAL_IMAGE_LAB_ID],true);
}

setTimeout(()=>{launchRealQuestionImageLab().catch(err=>console.error("Falha no laboratório com questão real.",err))},420);
'''

html = html.replace(MARKER, MARKER + real_lab, 1)
path.write_text(html, encoding="utf-8")
print(f"Real image question lab injected into {path}.")
