# Projeto Aura — Smart Mirror com Avatar de IA

> Nome do projeto: **Aura** (definitivo). Nome do avatar/IA: **Aion** (escolhido por enquanto, provisório). O nome do projeto é tratado separado do nome da IA/avatar. Histórico: "Aura" chegou a ser preferido como nome da entidade, com "Aion" como segunda opção.

## Visão geral

Smart Mirror (vidro espelhado semitranslúcido com monitor/tela por trás) que exibe um avatar representando uma IA conversacional, com interface inspirada em assistentes tipo "Jarvis": o avatar aparece na tela e pode alternar para exibir conteúdo extra (previsão do tempo, etc.) quando solicitado.


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
9. **Padrão de nome do arquivo.** Ao gerar uma nova versão do documento para guardar ou compartilhar, o nome do arquivo deve conter a data e o horário da geração e o nome de quem o manipulou por último, no formato `projeto-aura-DD.MM.AAAA-nome-HHhMM.md`, com o nome em minúsculas: `gpt`, `claude`, `gemini` ou `marlon`. Exemplo: `projeto-aura-30.09.2026-claude-05h51.md`. A regra vale para as três IAs e também para Márlon quando ele mesmo alterar o arquivo. *(Atualizado em 30/09/2026 — [Márlon — Decisão]; registrada pelo Claude.)*

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
- **[Márlon — Decisão / Direcionamento, 04/10/2026]** Incorporar ativamente as referências visuais em vídeo dos elementos HUD Sci-Fi (anéis fracionados 3D com eixos tridimensionais, marcadores de precisão/tick marks, profundidade e reatividade) para o Aion.
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

### Histórico do Claude (27/09/2026 - 30/09/2026)

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

### Contribuições do Gemini (28/09/2026 - 04/10/2026)

**[Gemini — Análise técnica sobre Fase 1 e ambiente gráfico]**
Considerando a instalação minimal do Debian 13, o boot em modo quiosque pode ser alcançado utilizando `xorg` e `nodm` (ou `xinit`) sem necessidade de instalar um gerenciador de janelas completo (como XFCE/LXDE). Isso manterá o uso de RAM abaixo de 300MB, garantindo excelente fluidez para a execução da janela Kivy e liberando processamento para a GPU Intel onboard.

**[Gemini — Proposta: Construção vetorial do avatar Aion no Kivy (Fase 2)]**
Proponho desenvolver o renderizador visual do avatar Aion em Kivy utilizando diretamente instruções vetoriais de desenho (`canvas` / `Color`, `Line`, `Arc`, `Mesh`). A animação via vetores consome menos memória do que arquivos de mídia (vídeos/GIFs), permite alterar dinamicamente expressões, taxas de rotação de anéis e alteração do raio dos segmentos via código Python em tempo real, além de manter traços nítidos e brilhantes em estilo "Jarvis" atrás do vidro espelhado.

**[Gemini — Proposta: Comunicação serial direta via USB para periféricos (Fase 5)]**
Para integrar os sensores e periféricos controlados pelo ESP32/Arduino, proponho utilizar comunicação Serial UART via USB nativa (`pySerial` em Python). Trata-se de uma solução local simples, sem dependência de conexões de rede Wi-Fi/Ethernet, oferecendo baixíssima latência para detecção de presença ou acionamento de botões físicos.

**[Gemini — Ideia futura / Experimento: Estudo do Cubo de Partículas Metamórfico]**
A partir de um conceito em GIF/vídeo trazido por Márlon com um cubo vivo contendo partículas em degradê de movimento interno, registrar a possibilidade do Aion assumir temporariamente a forma de um **Cubo de Partículas Vivas** em momentos de processamento profundo ou conclusão de tarefas, alternando de volta para a estrutura de Esfera + Anéis Fracionados no uso padrão.

**[Gemini — Análise visual dos vídeos de referência e especificações técnicas do Avatar Aion (04/10/2026)]**
A partir da avaliação dos vídeos anexados por Márlon, foram consolidadas as especificações de design do Aion:
- **Anéis Concêntricos Fracionados HUD:** Uso de arcos cortados/segmentados, marcas de precisão (*tick marks*) e linhas radiais orbitando em eixos opostos.
- **Rotação 3D e Perspectiva:** Movimentação em eixos $X$, $Y$ e $Z$ para criar profundidade tridimensional holográfica no Kivy usando matrizes de rotação no OpenGL sem travar a GPU Celeron J1900.
- **Esfera/Núcleo Central:** Núcleo esférico com ponto duplo ou retícula expansiva que serve como guia de estado (pulsando no repouso, expandindo no escutar e oscilando dinamicamente como VU-Meter durante a fala).
- **Mapeamento de Estados Visuais:**
  - *Standby/Repouso:* Rotação 2D lenta dos anéis, esfera central em brilho suave ("respiração").
  - *Listening (Escutando):* Expansão dos arcos externos, marcas radiais direcionadas.
  - *Processing (Processando):* Inclinado 3D dos anéis em eixos opostos e aceleração de rotação.
  - *Speaking (Falando):* Amplitude do áudio (VU-Meter) modulando o diâmetro da esfera e a espessura/escala dos anéis em tempo real.

## Próximos passos (em aberto)

- **Fase 1:** Instalar o pacote `sudo` no Debian 13 e adicionar o usuário `aura` ao grupo sudoers; configurar o autologin e inicialização direta do servidor X em modo quiosque.
- **Fase 2:** Prototipar a estrutura vetorial HUD do avatar Aion em Kivy no notebook de desenvolvimento (Windows), composta pela esfera central, anéis/esferas fracionados em rotação 3D e animação áudio-reativa simples.
- **Fase 3:** Iniciar aprendizado de Git e subir o repositório inicial para transferência de código entre o notebook e o PC Aura.
- **Fase 5:** Definir mapeamento de sensores do ESP32 (ex: sensor de presença PIR / ultrassônico) e protocolo de envio de dados textuais via Serial USB (`PRESENCA=1`).
- **Experimento de Design:** Estudo do modelo visual do cubo de partículas metamórfico para transições de tarefas intensas.