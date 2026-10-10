# Projeto Aura — Smart Mirror com Avatar de IA

> Nome do projeto: **Aura** (definitivo). Nome do avatar/IA: **Aion** (escolhido por enquanto, provisório). O nome do projeto é tratado separado do nome da IA/avatar. Histórico: "Aura" chegou a ser preferido como nome da entidade, com "Aion" como segunda opção.

## Visão geral

Smart Mirror (vidro espelhado semitranslúcido com monitor/tela por trás) que exibe um avatar representando uma IA conversacional, com interface inspirada em assistentes tipo "Jarvis": o avatar aparece na tela e pode alternar para exibir conteúdo extra (previsão do tempo, etc.) quando solicitado.


## Propósito e visão de longo prazo

**[Márlon — Contexto, 30/09/2026]** O Projeto Aura tem origem em uma tentativa antiga de Márlon, quando ele buscava usar a assistente virtual **Denise (Guile3D Studio)** para automação doméstica. O objetivo original era ter essa assistente disponível na TV da sala, integrada a toda a automação da casa (sensores, status de luzes e equipamentos, câmeras de vigilância) e também integrada ao carro — nesse caso, com um PC próprio rodando a assistente, trazendo informações do veículo via OBD2 e, quando solicitado, informações da casa. O projeto não avançou na época.

**[Márlon — Visão de longo prazo]** Aura deve, no futuro, ter características de funcionamento semelhantes às do projeto original: integração com a automação da casa e com o carro. A diferença é que, em vez de usar a TV da sala como tela, o avatar (Aion) terá sua própria tela de personificação — o Smart Mirror que está sendo construído nesta primeira etapa do projeto.

**[Claude — Registro]** Vale deixar explícito, para consulta futura pelas três IAs: o escopo imediato do Projeto Aura (Fases 1 a 5 descritas neste documento) cobre apenas o Smart Mirror com o avatar Aion. A integração com automação doméstica e com o carro via OBD2 é a visão de longo prazo que dá sentido ao projeto, mas ainda não tem fases, hardware ou arquitetura definidos — deve ser tratada como um horizonte a considerar nas decisões de arquitetura (por exemplo, ao pensar em como o Aion vai se comunicar com outros sistemas no futuro), sem que isso trave o progresso da etapa atual.

## Metodologia de colaboração entre Márlon, GPT, Claude e Gemini

Este documento é a **memória compartilhada e documento de continuidade do Projeto Aura**. Ele pode ser utilizado por Márlon e pelas três IAs participantes — GPT, Claude e Gemini — para manter o histórico de decisões, raciocínios, propostas, experimentos, pendências e evolução do projeto.

### Identificação das contribuições

Para evitar que ideias, análises e decisões sejam atribuídas incorretamente a outra pessoa ou IA, toda nova contribuição relevante deverá indicar sua origem:

- **[Márlon — Decisão]** — decisão ou definição feita pelo usuário.
- **[Márlon — Preferência]** — preferência, objetivo ou restrição declarada pelo usuário.
- **[GPT — Análise]** — análise técnica ou interpretação apresentada pelo GPT.
- **[GPT — Proposta]** — sugestão apresentada pelo GPT, ainda não considerada uma decisão.
- **[GPT — Decisão registrada]** — decisão que o GPT está apenas registrando após ter sido definida no processo do projeto; não significa que a decisão pertença ao GPT.
- **[Claude — Análise]** — análise técnica ou interpretação apresentada pelo Claude.
- **[Claude — Proposta]** — sugestão apresentada pelo Claude.
- **[Gemini — Análise]** — análise técnica ou interpretação apresentada pelo Gemini.
- **[Gemini — Proposta]** — sugestão apresentada pelo Gemini.

Quando uma ideia de uma IA for posteriormente adotada por Márlon, ela deverá continuar identificada como proposta originada daquela IA, enquanto a adoção deverá ser registrada separadamente como **[Márlon — Decisão]**.

### Regras para manutenção do documento

1. **Decisões não devem ser confundidas com propostas.** Uma sugestão discutida não se torna automaticamente uma decisão.
2. **Ideias descartadas devem permanecer registradas quando forem úteis para entender a evolução do projeto**, preferencialmente com a razão do descarte.
3. **Mudanças de decisão devem ser registradas**, preservando o histórico anterior em vez de simplesmente apagá-lo quando isso for relevante.
4. **Cada IA deve se referir a si mesma pelo próprio nome — GPT, Claude ou Gemini — nas contribuições que inserir no documento.**
5. Quando uma IA estiver analisando uma contribuição de outra IA, deverá deixar clara a origem. Exemplo: **[GPT — Análise sobre proposta do Claude]**.
6. **Márlon permanece como responsável pelas decisões do projeto.** As IAs atuam como colaboradoras técnicas, analíticas e criativas.
7. Sempre que possível, informações importantes devem ser organizadas em uma destas categorias: **Decisão, Proposta, Análise, Experimento, Resultado, Pendência ou Ideia futura**.
8. O documento deve funcionar como uma **fonte de continuidade**, permitindo que qualquer uma das três IAs retome o projeto sem depender da memória de uma conversa específica.
9. **Padrão de nome do arquivo.** Ao gerar uma nova versão do documento para guardar ou compartilhar, o nome do arquivo deve conter a data da geração, o nome de quem o manipulou por último e o horário da geração, no formato `projeto-aura-DD.MM.AAAA-nome-HHhMM.md`, com o nome em minúsculas: `gpt`, `claude`, `gemini` ou `marlon`, e o horário no formato simples de 24h (ex: `18h50`). Exemplo: `projeto-aura-28.09.2026-claude-18h50.md`. A regra vale para as três IAs e também para Márlon quando ele mesmo alterar o arquivo. *(Definida por Márlon em 28/09/2026, ajustada no mesmo dia para incluir o horário — [Márlon — Decisão]; registrada pelo Claude.)*

### Estado da metodologia

**[GPT — Proposta metodológica, aprovada por Márlon em 27/09/2026]**

A partir desta atualização, esta metodologia passa a ser a convenção de trabalho do Projeto Aura. Novas contribuições relevantes ao documento deverão respeitar essa identificação de autoria e a distinção entre propostas e decisões.

## Histórico de decisões

- **[Márlon — Decisão, 27/09/2026]** Seguir o Projeto Aura com a GPU integrada Intel (onboard) da placa-mãe ASRock Q1900M, em vez da GPU dedicada ASUS R5230. A R5230 está fisicamente instalada, mas não aparece no `lspci` (não é reconhecida pelo sistema); Márlon vai verificar depois se há alguma configuração na BIOS bloqueando o reconhecimento. Até lá, a placa será removida do PC do Projeto Aura.
- **[Márlon — Decisão, 28/09/2026]** A ASUS R5230 foi retirada do PC e não faz mais parte do projeto (substitui o plano anterior de investigar a BIOS). O vídeo é exclusivamente pela GPU integrada Intel.
- **[Márlon — Decisão, 28/09/2026]** O SSD do PC Aura foi formatado e o Windows removido; o Debian do projeto ocupa o SSD sozinho.
- **[Márlon — Decisão, 28/09/2026]** O nome do projeto continua "Aura"; o nome do avatar, por enquanto, será "Aion".
- **[Márlon — Decisão / Preferência, 28/09/2026]** O design visual do avatar Aion **não utilizará expressões faciais humanas ou rostos com olhos/bocas atrás do espelho**, para evitar o efeito "assustador" ou o "Vale da Estranheza" no ambiente doméstico. A representação será **abstrata e conceitual**, mantendo seriedade, mas com um dinamismo interessante e divertido de observar.
- **[Márlon — Preferência de Design, 28/09/2026]** O modelo visual do Aion terá como base uma **forma geométrica circular** com cor única estilo **neon**, contendo uma **esfera central e esferas/anéis fracionados (segmentados)** orbitando ao redor, apresentando variações dinâmicas e reatividade conforme o som da fala.
- **[Claude — Análise]** O `dmesg` confirmou que o driver `i915` reconheceu a GPU Intel (Bay Trail/Valleyview) e a inicializou como framebuffer principal sem nenhum erro — a base gráfica do sistema está funcional sem qualquer ajuste extra de driver.
- **[Claude — Registro de progresso]** Debian 13 (Trixie) instalado com sucesso no PC do Projeto Aura (hostname `aura`, usuário `aura`, instalação mínima sem ambiente de desktop). Por ora, o `sudo` não foi instalado (o instalador criou senha de root); Márlon está usando `su -` para comandos administrativos enquanto isso não é resolvido.
- Ideia original: cubo de LED RGB 16x16x16 para exibir o avatar — descartada por custo elevado.
- Segunda ideia: tela transparente comercial de 1,5" no ESP32 — ainda em aberto como alternativa, orçamento de até R$700.
- Avaliada e descartada a técnica de Pepper's Ghost/Pepper's Cone (exige pouca luz ambiente).
- Avaliado e descartado holograma por persistência de visão (POV fan) — não pode ficar ligado 24h.
- Avaliada e descartada a ideia de tela redonda só com "olhos" estilo robô.
- **Decisão atual:** smart mirror com vidro espelhado semitranslúcido (já em posse, ~50x30cm) e monitor/tela por trás.

## Arquitetura escolhida

- **[Márlon — Decisão, 27/09/2026]** A tela do Projeto Aura será usada em modo retrato (girada). Implementação da rotação fica para uma etapa futura, quando a configuração do X/Kivy for feita — não é prioridade agora.

- **"Cérebro" do sistema:** PC antigo (fanless) com Celeron, GPU integrada Intel e SSD, rodando Debian 13 minimal em modo quiosque.
- **Avatar:** desenvolvido em Python, usando **Kivy** como framework (Pygame foi cogitado, mas Kivy foi o escolhido).
- **ESP32 e Arduino Uno R3:** atuam como periféricos (sensores, botões, presença), não como processamento principal.
- **Fluxo de desenvolvimento:** edição do código em PC separado com Windows 11 (VSCode e PyCharm instalados), usando **Git** para transferir o código até o PC Linux onde o sistema realmente roda. O usuário ainda vai aprender Git ao longo do projeto.
- **Sistema operacional:** não domina bem Linux, vai precisar de apoio na implementação de todo o sistema.

## Hardware disponível

- **PC "cérebro" do Projeto Aura** (Debian 13 instalado sozinho no SSD, sem Windows):
  - Placa-mãe: ASRock Q1900M (Celeron quad-core embutido)
  - RAM: 4GB DDR3-1333 (Kingmax) — ampliação para 8GB planejada
  - Armazenamento: SSD Kingston SA400S37 480GB
  - Vídeo: GPU integrada Intel (onboard); a GPU dedicada ASUS R5230 foi removida e não faz mais parte do projeto
  - Fonte de alimentação: 140W
  - **Totalmente fanless** (sem cooler) — CPU e fonte de alimentação sem ventoinha; design original de fábrica, sem preocupação de aquecimento
- Tela LCD de 17" ou 19" — para testes iniciais.
- ESP32 antigo, com mais de 10 anos de uso.
- ESP32 DevKitV1 (módulo ESP-WROOM-32).
- Arduino Uno R3.
- Shield Ethernet HanRun (HR911105A) com leitor de cartão SD, compatível com Arduino Uno R3.
- Vidro espelhado semitranslúcido (~50x30cm) para o efeito de smart mirror.
- Material eletrônico diverso e componentes variados (a detalhar).

## Contribuições das IAs

### Histórico do Claude (27/09/2026 - 28/09/2026)

**[Claude — Análise sobre o problema do driver da GPU R5230]** *(histórico — superada: a R5230 foi removida do projeto em 28/09/2026)*
A ASUS R5230 usa o chip Radeon (série Cape Verde/Oland, GCN 1.0). No Windows 10/11 recente é comum esse modelo não ser mais reconhecido automaticamente, pois a AMD já descontinuou drivers novos para GPUs tão antigas. No Linux, porém, essa GPU é suportada nativamente pelo driver de código aberto `radeon` (ou `amdgpu` em modo legado, dependendo da distro), já incluído no kernel — normalmente funciona "out of the box" sem precisar instalar nada extra.

**[Claude — Análise sobre RAM e viabilidade do hardware]**
4GB de RAM já são suficientes para uma instalação mínima de Debian/Lubuntu rodando em modo quiosque com um único aplicativo Kivy em tela cheia (sem ambiente de desktop completo, sem navegador pesado). O upgrade para 8GB planejado dá folga confortável, mas não é bloqueante para começar os testes.

**[Claude — Proposta: roteiro de implementação em fases]**
Como o projeto já tem hardware e arquitetura decididos, mas ainda não tem nenhuma base de software rodando, proponho dividir a implementação em fases pequenas e testáveis, para não travar em decisões e começar a ver resultado prático rápido:

1. **Fase 1 — Base do sistema:** instalar Debian minimal (or Lubuntu) no PC Celeron, validar o vídeo (feito com a GPU integrada Intel, driver `i915` sem ajustes), configurar boot direto em modo quiosque (sem gerenciador de janelas completo).
2. **Fase 2 — Protótipo do avatar isolado:** no notebook de desenvolvimento (Windows), criar uma janela Kivy simples em tela cheia com uma forma/rosto placeholder (ex: um círculo com "olhos" animados), só para validar o fluxo de desenvolvimento e a performance, antes de desenhar o avatar definitivo.
3. **Fase 3 — Fluxo Git:** configurar um repositório Git simples (pode ser local ou GitHub privado) para transferir o protótipo do notebook até o PC Celeron, já usando esse projeto real como forma de aprender Git na prática.
4. **Fase 4 — Integração no espelho:** só depois do protótipo rodando estável no PC Celeron em modo quiosque, montar fisicamente o monitor atrás do vidro espelhado.
5. **Fase 5 — Periféricos:** conectar ESP32/Arduino como sensores de presença/botões, inicialmente apenas enviando dados simples (ex: via serial ou MQTT local) para o avatar reagir.

### Histórico do GPT (28/09/2026)

**[GPT — Análise sobre o estado atual e a sequência de implementação]**
O documento indica que a Fase 1 avançou: o Debian 13 está instalado, o sistema reconhece a GPU Intel integrada e a ASUS R5230 foi removida. Recomendo manter o próximo objetivo pequeno e verificável: concluir o acesso administrativo com `sudo` e validar uma sessão gráfica mínima antes de introduzir o Kivy. Isso ajuda a separar problemas do sistema gráfico de eventuais problemas do aplicativo.

**[GPT — Proposta: validar a compatibilidade gráfica antes de investir na animação]**
Antes de construir o avatar Aion com muitos efeitos, criar um protótipo Kivy muito simples e medir seu comportamento no hardware real: inicialização, uso de memória, fluidez e estabilidade por algumas horas. A GPU Intel integrada e o Celeron são antigos; por isso, não convém assumir antecipadamente que todos os efeitos ou caminhos de aceleração gráfica terão o desempenho esperado. O resultado do teste deve orientar a complexidade visual.

**[GPT — Análise sobre a proposta de uso de vetores para o avatar]**
A proposta de desenhar o avatar com instruções vetoriais do `canvas` do Kivy é coerente com um avatar dinâmico e escalável. Como ressalva, desenho vetorial não garante, por si só, menor consumo ou maior fluidez em todos os casos: a quantidade de elementos redesenhados, a frequência das animações e o caminho gráfico usado também importam. A sugestão é começar com poucos elementos — núcleo, olhos e brilho discreto — e acrescentar efeitos apenas depois de medir o protótipo.

**[GPT — Análise sobre a comunicação serial dos periféricos]**
A comunicação serial USB com `pySerial` é uma opção inicial simples para ligar o ESP32 ou Arduino ao PC localmente, sem depender de Wi-Fi ou Ethernet. Uma precisão terminológica: a porta serial apresentada por USB normalmente é uma interface serial UART encapsulada por um conversor USB-serial ou pela USB nativa do microcontrolador; isso não significa necessariamente sinalização elétrica RS-232. Para a primeira prova de conceito, basta definir mensagens textuais curtas e documentadas, por exemplo `PRESENCA=1`, e testar a reconexão após desligar e religar o periférico.

**[GPT — Proposta: critérios de conclusão por fase]**
Para tornar o avanço fácil de acompanhar entre as IAs, sugiro registrar cada fase com três itens: **objetivo**, **teste de aceitação** e **resultado observado**. Exemplo para a base gráfica: objetivo — abrir uma aplicação gráfica em tela cheia; teste — iniciar após reinicialização sem intervenção manual; resultado — registrar se funcionou e quais comandos/configurações foram necessários. Isso evita considerar uma etapa concluída apenas porque os pacotes foram instalados.

**[GPT — Proposta: registrar comandos e resultados do Debian]**
Durante a configuração do Debian, manter no documento ou em um arquivo auxiliar um pequeno diário técnico com os comandos relevantes e seus resultados, removendo senhas, tokens e outros dados sensíveis. Como o usuário está aprendendo Linux e Git durante o projeto, esse registro facilitará a retomada do trabalho e a comparação entre orientações das três IAs.

### Contribuições do Gemini (28/09/2026)

**[Gemini — Análise técnica sobre Fase 1 e ambiente gráfico]**
Considerando a instalação minimal do Debian 13, o boot em modo quiosque pode ser alcançado utilizando `xorg` e `nodm` (ou `xinit`) sem necessidade de instalar um gerenciador de janelas completo (como XFCE/LXDE). Isso manterá o uso de RAM abaixo de 300MB, garantindo excelente fluidez para a execução da janela Kivy e liberando processamento para a GPU Intel onboard.

**[Gemini — Proposta: Construção vetorial do avatar Aion no Kivy (Fase 2)]**
Proponho desenvolver o renderizador visual do avatar Aion em Kivy utilizando diretamente instruções vetoriais de desenho (`canvas` / `Color`, `Line`, `Arc`, `Mesh`). A animação via vetores consome menos memória do que arquivos de mídia (vídeos/GIFs), permite alterar dinamicamente expressões, taxas de rotação de anéis e alteração do raio dos segmentos via código Python em tempo real, além de manter traços nítidos e brilhantes em estilo "Jarvis" atrás do vidro espelhado.

**[Gemini — Proposta: Comunicação serial direta via USB para periféricos (Fase 5)]**
Para integrar os sensores e periféricos controlados pelo ESP32/Arduino, proponho utilizar comunicação Serial UART via USB nativa (`pySerial` em Python). Trata-se de uma solução local simples, sem dependência de conexões de rede Wi-Fi/Ethernet, oferecendo baixíssima latência para detecção de presença ou acionamento de botões físicos.

**[Gemini — Ideia futura / Experimento: Estudo do Cubo de Partículas Metamórfico]**
A partir de um conceito em GIF/vídeo trazido por Márlon com um cubo vivo contendo partículas em degradê de movimento interno, registrar a possibilidade do Aion assumir temporariamente a forma de um **Cubo de Partículas Vivas** em momentos de processamento profundo ou conclusão de tarefas, alternando de volta para a estrutura de Esfera + Anéis Fracionados no uso padrão.

## Próximos passos (em aberto)

- **Fase 1:** Instalar o pacote `sudo` no Debian 13 e adicionar o usuário `aura` ao grupo sudoers; configurar o autologin e inicialização direta do servidor X em modo quiosque.
- **Fase 2:** Prototipar a estrutura vetorial do avatar Aion em Kivy no notebook de desenvolvimento (Windows), composta por uma esfera central, anéis/esferas fracionados em rotação e animação áudio-reativa simples.
- **Fase 3:** Iniciar aprendizado de Git e subir o repositório inicial para transferência de código entre o notebook e o PC Aura.
- **Fase 5:** Definir mapeamento de sensores do ESP32 (ex: sensor de presença PIR / ultrassônico) e protocolo de envio de dados textuais via Serial USB (`PRESENCA=1`).
- **Experimento de Design:** Márlon disponibilizar o vídeo do cubo com partículas em degradê para análise de movimento e viabilidade no Kivy.
### Histórico do GPT — Análise da estilização do avatar Aion (28/09/2026)

**[GPT — Análise sobre a proposta visual da esfera central e dos anéis fracionados]**

A combinação de núcleo esférico com anéis ou esferas orbitais fracionadas é coerente com a preferência de Márlon por uma representação abstrata, geométrica e não antropomórfica. Recomendo preservar essa composição como identidade visual principal do Aion, procurando manter sua silhueta reconhecível mesmo em repouso, com brilho reduzido ou durante animações discretas.

O objetivo não deve ser apenas produzir um efeito visual atraente: os movimentos podem comunicar estados observáveis do sistema, como repouso, detecção de presença, interação, fala e transição entre telas. Esses estados devem ser suaves e distinguíveis, sem exigir que o usuário interprete uma linguagem visual excessivamente complexa.

**[GPT — Proposta de design: movimento responsivo sem aparência de visualizador musical]**

Durante a fala, o núcleo central pode pulsar de forma moderada, enquanto os anéis ou segmentos respondem à intensidade do áudio. Sugiro evitar que todos os elementos reajam com a mesma amplitude e velocidade, pois isso pode resultar em uma animação semelhante a um equalizador genérico. Uma combinação de movimento principal no núcleo e resposta secundária nos anéis pode criar uma impressão mais orgânica, mantendo a natureza geométrica do avatar.

A reação ao áudio deverá ser testada com fala real e ruído ambiente. Se a implementação inicial não tiver acesso ao áudio efetivamente produzido ou captado, a animação deverá ser identificada como uma simulação, não como sincronização de áudio concluída.

**[GPT — Proposta de design: estados visuais graduais]**

Proponho estudar uma pequena família de estados, sem os tratar ainda como decisões definitivas:

- **Repouso:** movimento lento e discreto, com brilho moderado.
- **Presença detectada / despertar:** aumento gradual de luminosidade e aceleração breve dos segmentos, seguido de estabilização.
- **Interação ou escuta:** movimento contido que indique que o sistema está ativo, sem sugerir compreensão perfeita do ambiente.
- **Fala do Aion:** pulsação do núcleo e resposta dos anéis à intensidade do áudio, quando houver sinal disponível para isso.
- **Transição ou tarefa visual especial:** transformação temporária da esfera em outra forma, caso a implementação e o significado sejam validados.

A paleta neon de cor única continua sendo a direção registrada por Márlon. Variações de intensidade, opacidade e brilho podem fornecer diferenciação inicial sem introduzir várias cores. A escolha exata da cor e os parâmetros de brilho permanecem em aberto.

**[GPT — Análise sobre a proposta Gemini do Cubo de Partículas Vivas]**

O Cubo de Partículas Vivas pode ampliar o repertório visual do Aion, mas recomendo mantê-lo como experimento secundário, e não como substituto da identidade esférica. Uma transformação temporária entre esfera e cubo poderia funcionar como transição visual ou recurso para situações específicas, desde que o usuário consiga reconhecer o Aion antes, durante e depois da transformação.

É importante não associar automaticamente o cubo a um suposto “processamento profundo” interno. O efeito só deverá representar um estado operacional se o software conseguir identificar esse estado de forma concreta; caso contrário, deverá ser tratado como recurso estético de transição ou como animação demonstrativa. A ideia ainda depende da análise do vídeo de referência mencionado por Márlon e de um teste de viabilidade no Kivy e no hardware real.

**[GPT — Análise: legibilidade no Smart Mirror]**

A aparência no monitor de desenvolvimento pode diferir bastante da aparência atrás do vidro espelhado. Reflexos, iluminação ambiente, distância de observação e contraste podem reduzir a leitura dos segmentos finos ou fazer o brilho parecer excessivo. Por isso, recomendo começar com formas simples, contornos nítidos e poucos elementos simultâneos. O brilho deve ser suficiente para destacar o avatar sem criar uma mancha luminosa que apague a geometria.

O protótipo deve ser avaliado primeiro no monitor e, posteriormente, atrás do vidro semitranslúcido disponível. A avaliação no vidro real será necessária antes de definir espessura dos traços, intensidade do brilho, quantidade de segmentos e velocidade das animações.

**[GPT — Proposta: critérios para avaliar o protótipo visual]**

Para cada versão do avatar, registrar:

1. **Reconhecimento:** a forma principal continua identificável em repouso e durante o movimento?
2. **Legibilidade:** os segmentos permanecem distinguíveis à distância normal de uso?
3. **Conforto visual:** o movimento é agradável por vários minutos, sem cintilação ou aceleração excessiva?
4. **Resposta:** a animação corresponde ao estado real do sistema ou ao sinal de áudio disponível?
5. **Desempenho:** a animação mantém fluidez e estabilidade no PC Celeron com gráficos Intel integrados?
6. **Smart Mirror:** o resultado continua legível atrás do vidro e sob a iluminação do ambiente?

Esses critérios são propostas de teste, não resultados já observados. A complexidade visual deverá crescer gradualmente, conforme os testes no hardware real.

### Atualização proposta para os próximos passos do design

**[GPT — Proposta; aguarda avaliação de Márlon]**

- Criar um protótipo estático da esfera central e dos anéis fracionados, sem efeitos adicionais, para fixar proporções e silhueta.
- Implementar uma animação de repouso simples e verificar a fluidez no Kivy.
- Acrescentar pulsação do núcleo e resposta dos anéis usando um sinal de áudio ou uma entrada simulada claramente identificada.
- Testar contraste e brilho atrás do vidro semitranslúcido.
- Só depois explorar a transformação para o Cubo de Partículas Vivas, usando o vídeo de referência para estudar movimento, densidade e transição.
- Registrar os resultados observados e as limitações do hardware antes de aumentar a quantidade de elementos ou efeitos.

**Estado:** todas as recomendações acima são contribuições analíticas e propostas do GPT. Não alteram as decisões de Márlon registradas anteriormente nem tornam o Cubo de Partículas Vivas parte definitiva do avatar.
## Atualização de decisão — comportamento do avatar Aion (28/09/2026)

**[Márlon — Decisão, 28/09/2026]** O Aion seguirá a abordagem de **presença digital responsiva**, e não apenas a de um objeto digital com animações decorativas. A detecção de presença, a escuta e a fala deverão provocar mudanças visuais coerentes com o estado real em que o sistema se encontra.

**[GPT — Registro da decisão de Márlon]** Esta decisão orienta o desenvolvimento do comportamento visual do avatar. As animações deverão refletir sinais e estados que o software realmente consegue identificar. Por exemplo, o estado de fala deve acompanhar a saída de áudio quando esse sinal estiver disponível; o estado de escuta deve corresponder ao funcionamento efetivo da captação ou do processamento de entrada; e a resposta à presença deve depender dos dados recebidos dos sensores. Quando algum estado ainda não estiver integrado, o protótipo deverá tratá-lo como simulação explicitamente identificada, não como funcionalidade concluída.

### Consequências práticas para o desenvolvimento

- **Presença detectada:** o Aion poderá sair gradualmente do repouso e indicar que percebeu a aproximação, desde que o sensor esteja integrado e tenha sinal válido.
- **Escuta:** a animação indicará que o sistema está efetivamente em estado de escuta ou captação, sem sugerir que compreendeu o usuário antes de haver processamento correspondente.
- **Fala:** o núcleo e os anéis poderão reagir ao áudio realmente emitido pelo sistema, quando houver acesso ao sinal de áudio.
- **Repouso:** manter uma animação discreta, sem representar atividade que não esteja ocorrendo.
- **Falhas ou indisponibilidade:** numa etapa futura, considerar uma indicação visual simples para estados como sensor desconectado, microfone indisponível ou áudio não iniciado, evitando que o avatar aparente estar funcionando normalmente quando não estiver.

**[GPT — Proposta de implementação]** Desenvolver inicialmente uma pequena máquina de estados visuais — por exemplo, `REPOUSO`, `PRESENCA`, `ESCUTANDO` e `FALANDO` — e definir quais eventos reais permitem entrar e sair de cada estado. A lista é uma proposta técnica inicial e poderá ser ajustada quando forem definidos os sensores, o caminho de áudio e a integração conversacional. Estados adicionais, como erro ou processamento, só deverão ser adicionados quando houver uma condição operacional clara para representá-los.

**Estado:** a abordagem de presença digital responsiva foi aprovada por Márlon. Os estados técnicos, os sensores específicos, a integração de áudio e as animações correspondentes ainda precisam ser implementados e testados.

## Contribuições do Claude — avaliação da identidade visual do Aion (28/09/2026)

**[Claude — Análise sobre viabilidade técnica no hardware]**
O conceito de esfera central com anéis/esferas fracionados orbitando, definido por Márlon e refinado por Gemini/GPT, é tecnicamente viável no hardware atual. A GPU integrada Intel do Celeron (geração Bay Trail, "Gen7") tem suporte a OpenGL ES 2.0 via driver Mesa incluído no Debian 13 — o mesmo `i915` que já apareceu no `dmesg` cobre também a parte 3D, não só o framebuffer. Isso significa que o backend gráfico do Kivy (SDL2 + OpenGL ES) deve rodar com aceleração de hardware real, e não cair para renderização por software. Para um desenho vetorial simples como o proposto (poucos círculos, arcos e linhas), isso deve sobrar folga de desempenho tranquilamente a 30–60 FPS, mesmo no Celeron antigo — a cautela do GPT em medir antes de investir em efeitos continua válida, mas o ponto de partida técnico é favorável, não incerto.

**[Claude — Avaliação da proposta de design]**
Concordo com a direção adotada: forma abstrata e geométrica evita o Vale da Estranheza, e a combinação núcleo + anéis fracionados com paleta neon de cor única é um bom equilíbrio entre simplicidade de implementação e impacto visual. Também concordo com a ressalva do GPT sobre desacoplar a amplitude de resposta entre núcleo e anéis para fugir do efeito "equalizador de som" — isso é o detalhe que mais separa um avatar com "presença" de um simples visualizador de áudio.

**[Claude — Proposta técnica de implementação no Kivy]**
Sugestões concretas para o protótipo da Fase 2, complementando os critérios já propostos pelo GPT:

- Desenhar cada anel como um grupo de instruções `canvas` próprio, envolto em `PushMatrix` / `Rotate` / `PopMatrix`, para que cada anel gire em velocidade independente sem recalcular a geometria a cada quadro — só o ângulo do `Rotate` muda.
- Para a pulsação do núcleo, evitar ligar a escala diretamente à amplitude bruta do áudio (fica "nervoso"); aplicar uma suavização tipo VU-meter (média móvel com ataque rápido e decaimento mais lento) para o efeito parecer uma respiração, não uma cintilação.
- Enquanto não houver captação/saída de áudio real integrada, simular a "fala" com um gerador de envelope sintético (ex: soma de senoides), mas identificar isso claramente como simulação no código e no documento — coerente com a decisão de Márlon sobre presença digital responsiva: nada deve parecer funcional antes de realmente estar.
- Ordem de construção sugerida: (1) esfera + anéis estáticos, só pra fechar proporção e silhueta; (2) rotação dos anéis; (3) pulsação simulada do núcleo; (4) troca da simulação pelo sinal de áudio real, só quando o caminho de áudio existir.

**[Claude — Análise sobre a proposta do Gemini/GPT de modo quiosque com nodm/xinit]**
Sem window manager, como o Gemini propôs, é a abordagem certa para esse caso — reforça o que eu já tinha sugerido antes de começar a instalação: um único app Kivy controlando sua própria janela em tela cheia não precisa de gerenciador de janelas. `nodm` é uma alternativa válida ao que eu tinha esboçado com `.bash_profile` + `startx`; qualquer um dos dois chega no mesmo resultado (login automático + X direto), fica a critério de qual for mais simples de configurar sem rede disponível ainda.

## Ideia trazida por vídeo — textura de partículas em 3D para o núcleo do Aion (30/09/2026)

**[Márlon — Ideia]** Vídeo de referência mostrando, em um display gráfico monocromático (aparentemente de uma bancada/case com indicadores de temperatura), um cubo formado por pontos/partículas em rotação contínua, com "espinhos" pontilhados irradiando das bordas — efeito visual que Márlon considera interessante para aproveitar no círculo/núcleo central do Aion.

**[Claude — Análise do efeito]** O vídeo mostra uma nuvem de pontos organizada como um cubo, vista em perspectiva isométrica, girando lentamente; as bordas têm pontos que se espalham para fora, dando uma textura "espinhosa"/orgânica em vez de uma superfície lisa. Comparando frames sequenciais do vídeo, a rotação é real (a face visível muda de orientação ao longo do tempo), não um efeito estático.

**[Claude — Avaliação de viabilidade]** Esse efeito é mais sofisticado do que os anéis 2D simples discutidos até aqui, mas continua viável no Kivy sem precisar de motor 3D (OpenGL 3D, malhas, etc.): basta manter uma nuvem de pontos em coordenadas 3D (ex: distribuídos sobre uma esfera, com um raio levemente aleatório por ponto para simular a textura "espinhosa" do vídeo), aplicar uma rotação simples (matriz de rotação em torno de um eixo, recalculada a cada quadro) e projetar cada ponto para 2D. O tamanho/opacidade de cada ponto pode variar conforme sua profundidade (z) após a rotação, criando a sensação de profundidade sem exigir uma engine 3D de verdade. Com algumas centenas de pontos — suficiente para reproduzir a densidade do vídeo — o custo de processamento é bem baixo, tranquilo para o Celeron do Projeto Aura.

**[Claude — Proposta]** Registrar esta ideia como uma variação a explorar na Fase 2, como alternativa (ou complemento) aos anéis fracionados já definidos: em vez de anéis sólidos girando ao redor do núcleo, o núcleo em si (ou uma camada dele) pode ser uma nuvem de pontos em rotação constante, com o mesmo princípio de nuvem-de-pontos podendo depois ser reaproveitado para dar textura aos próprios anéis. Sugiro tratar isso como uma opção de prototipagem a testar visualmente ao lado da proposta atual (esfera lisa + anéis), e não como substituição definitiva — a decisão de qual visual escolher fica para quando houver algo rodando na tela para comparação lado a lado.

## Marco concluído — boot em modo quiosque funcionando (02/10/2026)

**[Márlon — Registro]** O PC Aura foi reinstalado com Debian 13, desta vez com rede ativa durante a instalação, e configurado para rodar inteiramente como root (sem usuário separado, sem login manual), por preferência de simplicidade e como exercício de aprendizado em Linux.

**[Claude — Registro de progresso]** Infraestrutura de boot em modo quiosque validada e funcionando: login automático como root no tty1 (override do `getty@tty1.service`), X mínimo (`xserver-xorg` + `xinit`, sem gerenciador de janelas) iniciado automaticamente via `/root/.bash_profile`, com `/root/.xinitrc` desativando proteção de tela/DPMS e abrindo um app de teste (`xterm`) em tela cheia. Isso fecha a parte de infraestrutura da Fase 1. Próximo passo: substituir o `xterm` de teste pelo protótipo do Aion em Kivy (Fase 2), assim que ele existir e for transferido do notebook via Git (Fase 3).

## Marco concluído — ambiente de desenvolvimento Kivy validado no notebook (03/10/2026)

**[Márlon — Registro]** Ambiente de desenvolvimento do Aion configurado e testado com sucesso no notebook Windows 11: ambiente virtual Python dedicado, Kivy instalado, primeiro teste de janela ("Aion está vivo!") rodando corretamente. Git já instalado e configurado.

**[Claude — Nota técnica]** O notebook tem Python 3.14.6 como versão padrão do sistema, mas o Kivy estável (2.3.1) ainda não possui pacotes pré-compilados para o Windows nessa versão — só até Python 3.13. Para contornar isso sem mexer na instalação padrão do sistema, foi instalado o Python 3.12.0 à parte, e o ambiente virtual do projeto (`aura-env`, em `Documents\ProjetoAura`) foi criado especificamente com essa versão via `py -3.12 -m venv aura-env`. Também foi necessário excluir o Python/pip da varredura do antivírus Kaspersky instalado na máquina, que estava bloqueando a instalação.

**[Claude — Registro]** Foi gerado um guia próprio (fora deste documento compartilhado) com o passo a passo completo de implantação do ambiente no Windows, para o caso de Márlon precisar replicar a configuração em outro computador.

Próximo passo: esboçar a forma estática do núcleo do Aion (esfera central + anéis fracionados) em Kivy, antes de qualquer animação.

## Progresso do protótipo do Aion em Kivy — até a versão 3 (04/10/2026)

**[Márlon — Registro]** Primeiros esboços práticos do núcleo do Aion construídos e testados no notebook, em Kivy puro (sem Kivy Language/.kv por enquanto). Evolução validada até aqui:

- **Esboço 01 (forma estática):** núcleo central sólido + dois anéis fracionados ao redor, sem rotação nem pulsação. Ajustes aprovados: núcleo com o dobro do tamanho inicial, duas camadas de anéis (não três), e segmentos de cada anel com tamanhos e espaçamentos variados/aleatórios (não uniformes) — usando uma semente fixa de aleatoriedade para o padrão não mudar a cada execução.
- **Esboço 02 (rotação por anel):** cada anel passou a girar como um bloco rígido, em velocidade e sentido próprios. Feedback de Márlon: visualmente sem graça, por todos os segmentos de um mesmo anel se moverem sempre juntos.
- **Esboço 03 (rotação independente por segmento) — confirmado funcionando:** a abordagem mudou para cada segmento individual ter sua própria velocidade de rotação, sorteada dentro de uma faixa definida por anel. Isso faz os segmentos se espalharem e se reencontrarem ao longo do tempo, em vez de manterem sempre a mesma formação. Márlon validou este resultado ("Funcionou").

**[Márlon — Pedido em andamento, ainda não validado]** Sugestão feita para uma próxima versão (04): cada segmento também seguir um raio levemente diferente dentro da faixa do seu anel (não só velocidades diferentes), para que, ao se cruzarem, os segmentos passem em trajetórias distintas em vez de se sobreporem exatamente na mesma órbita.

**[Claude — Registro]** Comecei a implementar essa ideia (campo `raio_variacao` por anel, sorteando um raio próprio por segmento), mas a conversa foi interrompida pelo limite de uso do chat antes de terminar a implementação e testar com Márlon. **A versão 04 não está concluída** — o próximo passo é retomar esse ajuste a partir do esboço 03 (última versão validada), implementar o raio variável por segmento, gerar a versão 04 e validar com Márlon antes de seguir para a próxima etapa do roteiro (pulsação do núcleo).

## Contribuição do GPT e referência de imagem — esclarecimento de escopo (04/10/2026)

**[GPT — Contribuição, via Márlon]** GPT produziu uma análise textual da direção visual do Aion (núcleo com textura de partículas, anéis independentes, assinatura cromática ciano/preto-azulado, cinco estados de presença: repouso, despertar, escuta, fala, transição especial) e um roteiro de versões V04 a V07, alinhado com o que já estava em andamento neste documento (variação de raio por segmento como próximo passo, preservação da versão validada como ponto de recuperação, cautela em medir desempenho no PC Aura antes de assumir que efeitos de partículas serão fluidos).

**[GPT — Imagem de referência]** Junto com o texto, foi gerada uma imagem conceitual de tela cheia do "Aura Smart Mirror", mostrando um avatar **humanoide feminino fotorrealista** (rosto, expressões faciais, estilo realista) nomeado Aion, cercado por painéis laterais com clima, agenda, notícias, status da casa (luzes, câmeras, temperatura) e informações do carro.

**[Márlon — Decisão, 04/10/2026]** Da imagem gerada pelo GPT, o que interessa aproveitar é exclusivamente o **estilo e formato dos painéis laterais de informação** (clima, agenda, status da casa, carro) como referência de layout para quando esses dados forem integrados à tela do Aion. O **avatar humanoide fotorrealista não será adotado** — o projeto continua com o núcleo abstrato (esfera + anéis segmentados) já em desenvolvimento, no ritmo atual.

**[Claude — Registro]** Vale deixar explícito para as três IAs: um avatar humanoide fotorrealista exigiria modelagem 3D, rigging facial e animação de expressões — uma categoria de implementação bem diferente de desenhar vetores num canvas Kivy, e fora do que o hardware do PC Aura (Celeron antigo, vídeo integrado) foi dimensionado para sustentar. O roteiro técnico proposto pelo GPT (V04 órbitas orgânicas → V05 respiração do núcleo → V06 núcleo híbrido com partículas → V07 expressividade e áudio) continua válido e alinhado com o caminho já em andamento; os painéis de informação ao redor do núcleo abstrato ficam registrados como referência de layout a considerar futuramente, sem compromisso de design ainda.

## Versão 04 validada — órbitas orgânicas (04/10/2026)

**[Márlon — Registro]** Versão 04 do núcleo do Aion em Kivy (segmentos com raio e velocidade independentes) foi validada após uma rodada de ajustes finos:

- Raio de cada segmento passou a ser sorteado dentro de "fatias" iguais da faixa do anel (em vez de sorteio totalmente livre), eliminando tanto segmentos colados quanto espaçamento irregular demais entre órbitas vizinhas.
- Faixa de comprimento dos segmentos foi estreitada (`SEG_PESO_MIN` de 0.4 para 0.9, `SEG_PESO_MAX` de 1.6 para 1.4), alongando os segmentos menores para reduzir lacunas grandes que apareciam durante a órbita.
- Sentido de rotação passou a **alternar entre segmentos vizinhos** dentro do mesmo anel (um sim, um não), resolvendo o efeito de "cardume" — todos os segmentos de um anel girando na mesma direção, mesmo com velocidades diferentes, pareciam um grupo andando junto.
- Janela de teste ajustada para 600×760, por limitação de altura do desktop usado para desenvolvimento.

Com isso, a V04 do roteiro proposto pelo GPT está concluída e aprovada. Próximo item do roteiro: **V05 — respiração do núcleo** (pulsação suave de luminosidade/tamanho, inicialmente simulada).

## Mudança de direção visual — camadas tipo HUD/dial (05/10/2026)

**[Márlon — Referência]** Compartilhado um vídeo de referência (asset comercial de banco de imagens, estilo HUD/radar — não reproduzido aqui, apenas descrito) mostrando um padrão visual que reflete bem a preferência de Márlon para o Aion: núcleo central com conteúdo trocável (no vídeo, um globo terrestre; pode ser símbolo, efeito ou imagem), um anel de VU gráfico (barras radiais de alturas variadas) colado diretamente na borda do núcleo representando o áudio, e uma camada externa com marcações, mais estática, dando profundidade tridimensional e bonita vista de frente — podendo incorporar os segmentos orbitando já construídos (V01-V04).

**[Márlon — Decisões, 05/10/2026]**
- A pulsação do núcleo (introduzida na V05) foi **removida** — o anel de VU na borda do núcleo passa a ser a representação visual do áudio, tornando a pulsação redundante.
- O centro do núcleo deve, no futuro, exibir um **símbolo de expressão** relacionado ao que o áudio está "dizendo" — ideia inspirada em abreviações usadas em mensagens de texto (ex: "?!" para dúvida, "kkk" para humor). Fica registrado como direção futura, **não implementado ainda**.
- Para agora, aprovado implementar: (2) anel de VU na borda do núcleo, (3) manter os anéis de segmentos orbitando já validados na V04, (4) acrescentar um anel externo estático tipo mostrador/dial.

**[Claude — Registro da V06]** Implementada a reestruturação em camadas, do centro para fora: núcleo estático (sem pulsação) → anel de VU (barras radiais com amplitude simulada por envelope de ataque/decaimento independente por barra, mesmo princípio técnico da V05, agora aplicado por barra) → anéis de segmentos orbitando da V04 (reposicionados mais para fora, para abrir espaço ao VU) → anel externo estático com marcações regulares tipo mostrador/bússola. Ainda não validado visualmente por Márlon.

## Mudança de rumo no design do Aion (06/10/2026)

**[Márlon — Decisão]** Depois de ouvir a opinião da esposa sobre a V12 (ela viu o núcleo como "uma lâmina de microscópio cheia de micróbios"), Márlon decidiu mudar o rumo do design. A avaliação externa foi importante: o Aion precisa parecer um avatar/personagem reconhecível, e o caminho de camadas tipo HUD (V06 a V12 — núcleo, VU, anéis orbitando, dial, raios estruturais, gradiente de corpo, globo/dígitos binários) não estava alcançando isso.

**Novo conceito, deliberadamente simples:**
- Mantém apenas o núcleo com o degradê interno (escuro no centro, clareando perto da borda) — a única parte aproveitada de todo o trabalho anterior.
- Todo o resto (VU, anéis de segmentos, anel externo/dial, raios estruturais, gradiente de corpo, globo/dígitos binários) foi **removido**.
- No lugar do conteúdo central, um **gráfico de ondas senoidais representando as frequências da fala** (amplitude simulada por enquanto, mesmo princípio de ataque/decaimento já validado em versões anteriores).

**[Márlon — Restrição prática importante]** O monitor do PC Aura vai ficar atrás de um **vidro espelhado semi-translúcido** (lembrete: essa é a montagem física do Smart Mirror definida desde o início do projeto). Isso significa que efeitos visuais sutis — glow, halos, gradientes fracos, linhas finas de baixa opacidade — **não aparecem** através do vidro. Por isso, a partir de agora, as cores devem ser **sólidas** (alpha = 1, sem transparência), e qualquer elemento visual precisa ter contraste forte para sobreviver ao vidro.

**[Márlon — Plano]** Refinar essa versão simplificada primeiro, para poder seguir com as outras configurações do PC Aura (Fase 1 em diante). A sofisticação visual (o caminho das V06-V12, ou outro) fica para uma etapa futura, quando houver um computador mais forte para o Projeto Aura.

**[Claude — Registro]** As versões V06 a V12 (estrutura em camadas tipo HUD) permanecem registradas neste documento como histórico de exploração, mas não fazem mais parte do caminho ativo do projeto. A V13 (núcleo + onda senoidal, cores sólidas) é o novo ponto de partida.

## Núcleo com áudio real: da V14 ao osciloscópio da V17 (07 e 08/10/2026)

**[Márlon — Validação]** A V14 (núcleo dobrado + onda reagindo ao áudio do microfone) funcionou como proposto. Márlon também testou o código no celular **atrás do vidro espelhado real** que será usado no projeto: "fantástico, muito bonito", e até o degradê do núcleo ficou bem definido através do espelho. Isso confirma a decisão de simplificar (cores sólidas, alto contraste) e valida o degradê do núcleo como elemento que sobrevive ao vidro.

**[Márlon — Pedidos após a V14]** (1) capturar o áudio direto do computador (o que a placa de som reproduz, independente do volume do sistema) em vez do microfone; (2) a onda tinha um movimento lento e leve independente do sinal real, o que atrapalhava com áudio ativo — preferia um analisador mais "espectral", mais fiel e um pouco mais rápido; (3) linha um pouco grossa; (4) experimentar três linhas sobrepostas, cada uma numa faixa de frequência.

**[Claude — V15/V16]** Áudio do PC via loopback WASAPI do Windows, com a biblioteca PyAudioWPatch (`pip install PyAudioWPatch numpy`; a `sounddevice` usada na V14 não captura a saída de áudio do Windows). Pela documentação da Microsoft o loopback é capturado antes do volume do sistema, mas na prática isso pode variar conforme o dispositivo de saída (alto-falantes, fone, HDMI, Bluetooth) — precisa ser testado. Analisador de espectro real (FFT de 4096 pontos, escala logarítmica de frequência, ganho automático por pico recente, piso de ruído para o silêncio ficar reto). Na V16: três modos de linha (`uma_linha`, `tres_lado_a_lado`, `tres_sobrepostas`), simulação desligável (`PERMITIR_SIMULACAO`) e a fonte do áudio exibida no título da janela.

**[Márlon — Feedback da V15]** As três linhas sobrepostas causaram confusão visual. Além disso, a simulação (que entra automaticamente quando as bibliotecas de áudio não estão instaladas) atrapalhava a avaliação — por isso foi pedido poder desligá-la. Registro: a V15 provavelmente foi avaliada em modo simulado, pois as instruções de instalação das bibliotecas não chegaram a Márlon a tempo (conversa interrompida pelo limite de uso do chat). Uma prévia feita pelo Claude com sinal parecido com música confirmou, de qualquer forma, que três linhas sobrepostas ficam confusas mesmo com áudio real.

**[Márlon — Decisão, 08/10/2026]** Abandonar o analisador de espectro (frequência) e adotar um traçado estilo **osciloscópio / papel de eletrocardiograma**: amplitude em função do tempo, **uma única linha fina e sólida**, que caminha continuamente (da direita para a esquerda ou vice-versa), mostrando na parte central a amplitude do momento.

**[Claude — V17]** Implementada: a linha mostra o pico (com sinal) do áudio a cada 12,5 ms; o "papel" nunca para (sem áudio, a linha fica reta mas continua andando). A "caneta" (momento atual) fica por padrão no centro do núcleo, o histórico caminha para a esquerda e o trecho à frente da caneta é uma linha reta; tudo ajustável por constantes (`OSC_POSICAO_AGORA`, `OSC_SENTIDO`, `OSC_JANELA_SEG`, `OSC_RETA_A_FRENTE`). A interpretação de "parte central" (caneta no centro vs. na borda) está pendente de confirmação por Márlon. A V16 (espectro) permanece no histórico como alternativa. Status: aguardando teste de Márlon.
