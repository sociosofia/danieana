# Question Audit Pipeline

Pipeline independente para auditar em escala bancos de questões de Sociologia e, futuramente, Filosofia.

**Este repositório não faz parte do Sociosofia e não deve ser acoplado ao repositório do site.**
O vínculo com os simuladores ocorre apenas por arquivos exportados de questões aprovadas.

## Objetivo

Trocar auditoria manual questão a questão por uma esteira com exceções:

`raw -> hard gates -> deterministic evidence -> 3 independent model passes -> AUTO_READY / REVIEW / HOLD`

- `AUTO_READY`: consenso 3/3, confiança média alta, sem flags graves.
- `REVIEW`: maioria 2/3, confiança intermediária ou algum sinal de ambiguidade.
- `HOLD`: cancelada, truncada, imagem bloqueada no primeiro estágio, divergência forte ou estrutura inválida.

Nenhum status de modelo é renomeado como "gabarito oficial". A proveniência fica explícita.

## Segurança epistemológica

A ordem de autoridade é:

1. gabarito oficial definitivo, quando importado por um resolvedor documental;
2. tentativa conhecida como correta no banco;
3. duplicata/texto alinhado a questão já resolvida;
4. consenso independente de modelos;
5. revisão humana;
6. hold.

A versão inicial implementa 2 e 4–6. Importadores documentais podem ser plugados depois sem mudar o motor.

## Configuração

Crie o secret do repositório:

- `OPENAI_API_KEY`

Opcionalmente crie a variável:

- `OPENAI_MODEL=gpt-5-mini`

A chave deve ficar em GitHub Secrets, nunca no código. O SDK oficial também lê `OPENAI_API_KEY` do ambiente.

## Automação

O workflow `Question audit pipeline` roda duas vezes por hora e também aceita execução manual.
Cada execução processa um lote, grava checkpoint e envia de volta ao repositório:

- `data/state/results.jsonl`
- `data/output/summary.json`
- `data/output/auto_ready.json`
- `data/output/review.json`
- `data/output/hold.json`

Se a execução cair no meio, a próxima continua dos IDs ainda não presentes no estado.

Um segundo workflow diário repassa somente itens `REVIEW`, no máximo 3 vezes por questão. `HOLD` não entra em loop automático. Isso implementa a ideia de passar o sistema novamente sem gastar indefinidamente com casos ruins.

## Taxonomia

A taxonomia fina do SESI fica deliberadamente fora desta etapa.
Para o simulador, Sociologia usa quatro portas amplas:

1. Sociedade e Sociologia
2. Cultura e desigualdades
3. Poder e cidadania
4. Trabalho e mundo contemporâneo

A classificação segue `objeto principal cobrado -> conceito/autor -> tags`, evitando classificar pelo vocabulário periférico.

## Filosofia depois

Para Filosofia, cria-se apenas `config/disciplines/philosophy.json` com portas, subtemas e regra de classificação. Motor, estados, workflows, consenso e benchmark permanecem os mesmos.

## Benchmark antes de confiar no AUTO_READY

O script `question_audit.benchmark` compara resultados contra um arquivo de questões já auditadas.
O threshold recomendado no relatório é **>= 97% de precisão entre itens que o próprio sistema marcou AUTO_READY** antes de qualquer integração automática ao app.

O benchmark mede precisão da zona que será automatizada, não apenas acurácia média do modelo.

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
export OPENAI_API_KEY=...
python -m question_audit.pipeline --limit 20
python -m question_audit.export
```

## Separação de responsabilidades

Este repo produz um estoque auditado. Ele **não publica no Sociosofia** e **não modifica o app automaticamente**.
A integração com o Simulados da Ana & Dani deve consumir apenas `AUTO_READY` ou itens revisados, em etapa separada e reversível.
