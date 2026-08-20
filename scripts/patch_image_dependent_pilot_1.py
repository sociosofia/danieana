#!/usr/bin/env python3
from pathlib import Path
import json
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

MARKER = "const PILOT_IMAGE_BATCH_1="
if MARKER in html:
    print("Image-dependent pilot 1 already present; nothing to do.")
    raise SystemExit(0)

if 'id="danieana-image-support-style"' not in html:
    raise SystemExit("Pilot patch aborted: production image support is not present.")

questions = [
    {
        "id": "PILOT-4000245684",
        "sourceQuestionId": "4000245684",
        "discipline": "sociologia",
        "text": "A fotografia é do antropólogo Bronislaw Malinowski (1884-1942) durante seu convívio com os habitantes das Ilhas Trobriand, na Melanésia, período em que pôde fazer uma descrição inédita da vivacidade de uma cultura. Fruto desse trabalho, Malinowski publicou, em 1922, a obra Argonautas do Pacífico ocidental. Um parágrafo clássico da introdução do livro dá o sabor de sua narrativa: “Imagine-se o leitor sozinho, rodeado apenas de seu equipamento, numa praia tropical próxima a uma aldeia nativa, vendo a lancha ou o barco que o trouxe afastar-se no mar e desaparecer de vista. Tendo encontrado um lugar para morar no alojamento de algum homem branco – negociante ou missionário – você nada tem a fazer a não ser iniciar imediatamente seu trabalho...” Nesse contexto, o antropólogo inaugura um método de pesquisa que, a partir de então, passou a ser amplamente utilizado. Trata-se do método",
        "support": "",
        "images": [{"url": "./media/pilot/q_4000245684.png", "context": "enunciado", "alt": "Fotografia de Bronislaw Malinowski durante trabalho de campo entre habitantes das Ilhas Trobriand"}],
        "options": [
            {"label": "A", "text": "missionário"},
            {"label": "B", "text": "positivista"},
            {"label": "C", "text": "etnocêntrico"},
            {"label": "D", "text": "etnográfico"}
        ],
        "correct": 3,
        "gabarito": "D",
        "category": "sociedade",
        "subtopic": "Antropologia e etnografia",
        "origin": "Simulado UERJ · 2022",
        "institution": "Simulado UERJ",
        "year": 2022,
        "answer_type": "MULTIPLE_CHOICE",
        "difficulty_band": "Intermediária",
        "solution": "O trabalho de campo prolongado e a observação direta da vida social caracterizam o método etnográfico associado a Malinowski."
    },
    {
        "id": "PILOT-4000146570",
        "sourceQuestionId": "4000146570",
        "discipline": "sociologia",
        "text": "Observe a imagem a seguir. Percebe-se nela que a sociedade prevalece sobre as ações dos indivíduos, aprisionando-os. Dessa forma, o conteúdo da imagem representa um objeto de estudo da Sociologia, constituído historicamente como um conjunto de relações entre os homens na vida em sociedade. Sobre as características do objeto de estudo apresentado, é CORRETO afirmar que",
        "support": "Imagem originalmente indicada pela UPE e disponibilizada pelo Blog do Professor Henry.",
        "images": [{"url": "./media/pilot/q_4000146570.jpeg", "context": "enunciado", "alt": "Ilustração em que a sociedade aparece exercendo pressão sobre indivíduos"}],
        "options": [
            {"label": "A", "text": "Karl Marx elaborou o que considerava a relação indivíduo-sociedade como um conjunto de condições materiais manipuladas pelos indivíduos, objetivando organizar e manter as relações sociais de produção."},
            {"label": "B", "text": "a ação individual é o principal conceito desse objeto e só faz sentido na consciência de classe, possibilitando aos grupos mais ricos atuarem sobre os grupos mais pobres, aumentando a desigualdade social."},
            {"label": "C", "text": "as normas, os comportamentos e as regras são os aspectos fundantes do objeto em destaque. Seguidos pelos indivíduos, esses aspectos da vida social são construídos fora das consciências individuais para manter a sociedade coesa."},
            {"label": "D", "text": "a conduta dos indivíduos é valorizada, pois a ação individual tem mais importância que a imposição coercitiva das normas sociais."},
            {"label": "E", "text": "Max Weber criou o que denominou à ‘ação do indivíduo’, orientada pela ação de outros e estabelecida por uma relação significativa."}
        ],
        "correct": 2,
        "gabarito": "C",
        "category": "sociedade",
        "subtopic": "Durkheim e fato social",
        "origin": "Universidade de Pernambuco - UPE · 2017",
        "institution": "Universidade de Pernambuco - UPE",
        "year": 2017,
        "answer_type": "MULTIPLE_CHOICE",
        "difficulty_band": "Sem estimativa",
        "solution": "A alternativa C descreve exterioridade, generalidade e coerção: características centrais do fato social em Durkheim."
    },
    {
        "id": "PILOT-4000037773",
        "sourceQuestionId": "4000037773",
        "discipline": "sociologia",
        "text": "Observe a tabela a seguir elaborada por Pierre Bourdieu. Com base na tabela, é correto afirmar:",
        "support": "Adaptado de BOURDIEU, P. Distinction, apêndice 3, Tabela A6; em ALMEIDA, H. B.; SZWAKO, J. E. (orgs.), Diferenças, Igualdade, 2009.",
        "images": [{"url": "./media/pilot/q_4000037773.png", "context": "enunciado", "alt": "Tabela de Pierre Bourdieu comparando gostos e práticas sociais entre classes"}],
        "options": [
            {"label": "A", "text": "A pesquisa sobre as classes sociais indica as similitudes e simetrias dos gostos e práticas sociais das classes baixas, médias e superiores."},
            {"label": "B", "text": "A pesquisa sobre as classes baixas, médias e altas revela o quanto a dimensão cultural dificilmente coincide com a dimensão econômica das diferenças."},
            {"label": "C", "text": "A pesquisa sobre a dimensão cultural das classes sociais demonstra que há diferenças nos seus estilos de vida e de consumo."},
            {"label": "D", "text": "A pesquisa sobre as classes sociais e suas hierarquias desautorizam as afirmações sobre possíveis assimetrias nas escolhas de consumo."},
            {"label": "E", "text": "A pesquisa sobre o consumo e as prática sociais das três classes denuncia a apropriação da cultura popular pelas classes superiores."}
        ],
        "correct": 2,
        "gabarito": "C",
        "category": "desigualdade",
        "subtopic": "Bourdieu, distinção e consumo",
        "origin": "Universidade Estadual de Londrina - UEL · 2010",
        "institution": "Universidade Estadual de Londrina - UEL",
        "year": 2010,
        "answer_type": "MULTIPLE_CHOICE",
        "difficulty_band": "Sem estimativa",
        "solution": "A tabela evidencia diferenças sistemáticas de gostos e práticas entre posições de classe, ligando distinção cultural, estilo de vida e consumo."
    },
    {
        "id": "PILOT-4000305647",
        "sourceQuestionId": "4000305647",
        "discipline": "sociologia",
        "text": "O direito social do cidadão representado na charge demanda a adoção de qual medida?",
        "support": "",
        "images": [{"url": "./media/pilot/q_4000305647.png", "context": "enunciado", "alt": "Charge do ENEM relacionada ao direito social à moradia"}],
        "options": [
            {"label": "A", "text": "Expansão da jornada laboral."},
            {"label": "B", "text": "Valorização do trabalho informal."},
            {"label": "C", "text": "Ampliação do acesso à habitação."},
            {"label": "D", "text": "Construção de alojamentos públicos."},
            {"label": "E", "text": "Edificação de condomínios elitizados."}
        ],
        "correct": 2,
        "gabarito": "C",
        "category": "desigualdade",
        "subtopic": "Direitos sociais e habitação",
        "origin": "Exame Nacional do Ensino Médio - ENEM · 2024",
        "institution": "Exame Nacional do Ensino Médio - ENEM",
        "year": 2024,
        "answer_type": "MULTIPLE_CHOICE",
        "difficulty_band": "Acessível",
        "solution": "A charge remete ao direito social à moradia; a medida compatível é ampliar o acesso à habitação."
    },
    {
        "id": "PILOT-4000084413",
        "sourceQuestionId": "4000084413",
        "discipline": "sociologia",
        "text": "Observe a imagem a seguir. As diferentes formas de classificação e julgamento da realidade social são parte constitutiva do etnocentrismo. Sobre o etnocentrismo e os estudos sobre diferenças culturais, assinale a alternativa correta.",
        "support": "Imagem originalmente publicada em Um Sábado Qualquer; acesso indicado pela banca em 29 jun. 2014.",
        "images": [{"url": "./media/pilot/q_4000084413.png", "context": "enunciado", "alt": "Charge que contrasta modos diferentes de avaliar culturas e costumes"}],
        "options": [
            {"label": "A", "text": "A capacidade das ciências para a produção de verdades, imparciais e racionais, garantiu, nas mais diferentes épocas históricas, a contínua desnaturalização e desmitificação do etnocentrismo."},
            {"label": "B", "text": "O etnocentrismo é uma prática social de dominação cultural, cuja raiz histórica originou-se na sociedade moderna ocidental, com a eugenia e o nazismo em países europeus, a partir da década de 1930."},
            {"label": "C", "text": "O etnocentrismo caracteriza-se por formas extremas de intolerância cultural, religiosa e política, quando se expressam em condutas explícitas e irracionais de rejeição ao grupo dominado."},
            {"label": "D", "text": "O etnocentrismo corresponde a uma visão segundo a qual os valores próprios de um grupo é o centro de todas as coisas e todos os outros grupos são medidos e avaliados em relação a esses valores."},
            {"label": "E", "text": "O evolucionismo do século XIX, ao propor os estágios de um desenvolvimento unilinear, permitiu a ruptura com o etnocentrismo e com a ideia de superioridade do grupo dominante."}
        ],
        "correct": 3,
        "gabarito": "D",
        "category": "sociedade",
        "subtopic": "Etnocentrismo e relativismo cultural",
        "origin": "Universidade Estadual do Centro-Oeste - Unicentro · 2015",
        "institution": "Universidade Estadual do Centro-Oeste - Unicentro",
        "year": 2015,
        "answer_type": "MULTIPLE_CHOICE",
        "difficulty_band": "Sem estimativa",
        "solution": "Etnocentrismo é avaliar outros grupos tomando os valores do próprio grupo como centro e padrão de medida."
    }
]

payload = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
logic = f'''\nconst PILOT_IMAGE_BATCH_1={payload};\nconst PILOT_IMAGE_BATCH_1_IDS=PILOT_IMAGE_BATCH_1.map(q=>q.id);\n\nasync function launchImageDependentPilot1(){{\n  const params=new URLSearchParams(location.search);\n  if(params.get("imagePilot")!=="1")return;\n  for(const q of PILOT_IMAGE_BATCH_1){{\n    if(!QUESTIONS.some(existing=>existing.id===q.id))QUESTIONS.push(q);\n  }}\n  localStorage.removeItem(K.active);\n  S.study="area";S.discipline="sociologia";S.format="training";S.timer=false;S.count=PILOT_IMAGE_BATCH_1.length;S.fresh=false;\n  await start(PILOT_IMAGE_BATCH_1_IDS,true);\n}}\n\nsetTimeout(()=>{{launchImageDependentPilot1().catch(err=>console.error("Falha no piloto IMAGE_DEPENDENT 1.",err))}},350);\n'''

anchor = html.rfind("\nupdateModePanels();")
if anchor < 0:
    raise SystemExit("Pilot patch aborted: startHumanasApp closing anchor not found.")

html = html[:anchor] + logic + html[anchor:]
path.write_text(html, encoding="utf-8")
print(f"Image-dependent pilot 1 injected into {path}.")
