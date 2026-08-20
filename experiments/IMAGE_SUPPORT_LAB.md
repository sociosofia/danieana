# Laboratório de imagens do Dani&Ana

Esta branch testa suporte a imagens em questões sem alterar a versão publicada em `main`.

O laboratório valida:

- detecção de imagens somente nas questões selecionadas;
- pré-download antes do início do simulado;
- mensagem `Baixando imagens das questões…` com progresso;
- armazenamento no Cache Storage (`ana-dani-question-images-v1`);
- exibição responsiva no celular e no desktop;
- toque/clique para ampliar e novo toque/clique para fechar;
- retomada de sessão usando a imagem já armazenada.

A rota experimental usa `?imageLab=1` e injeta uma questão sintética com uma imagem SVG local. O objetivo desta etapa é validar o mecanismo sem depender ainda de CORS, disponibilidade ou formato das imagens de terceiros.

Depois de validado o mecanismo, as questões reais com imagem podem ser reincorporadas gradualmente. Para produção, a opção preferível é servir as imagens pelo mesmo domínio do PWA (ou por armazenamento com CORS controlado), mantendo o download sob demanda e o cache no aparelho.
