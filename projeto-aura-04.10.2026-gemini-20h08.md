# Projeto Aura — Documento Mestre de Desenvolvimento

## 1. Visão Geral do Projeto
O **Projeto Aura** consiste no desenvolvimento de um **Smart Mirror** (espelho inteligente) alimentado por uma inteligência artificial chamada **Aion**. 

### Princípios de Design e Interação
* **Presença Digital Responsiva:** O Aion não simula emoções falsas ou comportamentos antropomórficos complexos sem propósito[cite: 1].
* **Ergonomia Visual sem Rosto Humano:** A utilização de rostos humanos ou "olhos flutuantes" atrás do vidro espelhado é evitada para não causar o efeito *Vale da Estranheza* (*Uncanny Valley*) ou sensação de perturbação no ambiente residencial.
* **Estética HUD Neon Abstrata:** O avatar é fundamentado em geometria vetorial 3D de alta precisão (estilo HUD/Sci-Fi), composta por uma esfera central e anéis concêntricos fracionados que orbitam em eixos independentes[cite: 2, 3, 4], destacando-se sobre o fundo preto absoluto (#000000) do monitor.

---

## 2. Conceituação e Especificação Visual do Avatar Aion

### 2.1. Análise dos Vídeos de Referência e Elementos Estéticos
A partir da avaliação do material em vídeo fornecido para o projeto[cite: 2, 3], estabeleceu-se a estrutura visual oficial do Aion:

1. **Esfera Central / Núcleo Volumétrico:**
   * Representa o "ponto de consciência" ou a origem da IA[cite: 2, 3].
   * Contém um elemento interno (globo/retícula ou ponto duplo expansivo) que pulsa suavemente[cite: 2, 3].
2. **Anéis e Arcos Fracionados (Segmentados):**
   * Estruturas circulares interrompidas (com *gaps*) e marcadores de precisão (*tick marks*)[cite: 2, 3].
   * Movimentam-se em velocidades e eixos ($X$, $Y$, $Z$) opostos, criando uma sensação de rotação 3D e profundidade holográfica atrás do vidro semitranslúcido[cite: 2, 3, 4].
3. **Palette de Cor Neon Única:**
   * Utilização de tom único neon de alto contraste (ex.: Ciano/Azul elétrico `#00FFFF` ou `#0088FF`)[cite: 2, 3, 4] para atravessar a película espelhada com nitidez[cite: 1], permitindo pontos secundários em tom de destaque (ex.: Laranja/Amber) para alertas de sistema[cite: 3].

### 2.2. Mapeamento dos Estados de Comportamento do Aion

| Estado do Sistema | Comportamento Visual dos Anéis | Comportamento do Núcleo Central |
| :--- | :--- | :--- |
| **Standby / Repouso** | Anéis fracionados em rotação 2D lenta e constante em sentidos opostos[cite: 2, 3, 4]. | Pulsação suave (estilo "respiração" em frequência baixa)[cite: 1, 4]. |
| **Listening (Escutando)** | Expansão dos anéis externos; arcos projetam traços radiais e alinham-se em foco[cite: 3]. | Aumento da intensidade de brilho do núcleo[cite: 4]. |
| **Processing (Processando)** | Transição para rotação 3D em eixos inclinados ($X, Y, Z$) com aceleração e reorganização de segmentos[cite: 2, 4]. | Flutuação de partículas internas ou retícula em micro-movimento[cite: 2, 4]. |
| **Speaking (Respondendo)** | Modulação de amplitude nos arcos e anéis (comportamento de VU-meter/áudio-reativo)[cite: 1, 4]. | Expansão/contração direta em sincronia com o tom de voz[cite: 1, 4]. |

---

## 3. Arquitetura de Hardware e Software

### 3.1. Hardware
* **Processador:** Intel Celeron J1900[cite: 1, 4]
* **Memória RAM:** 4 GB DDR3[cite: 1, 4]
* **Armazenamento:** SSD 120 GB[cite: 1]
* **GPU:** Intel HD Graphics integrada (driver `i915`)[cite: 1, 4]
* **Exibição:** Monitor alinhado atrás de vidro espelhado semitranslúcido[cite: 1, 4]

### 3.2. Stack de Software
* **Sistema Operacional:** Debian 13 (Testing/Trixie) minimalista (sem ambiente de desktop pesado como GNOME/XFCE)[cite: 1, 4].
* **Servidor Gráfico:** Servidor X minimalista (`xorg` + `nodm` / `xinit`) executando a aplicação diretamente[cite: 1, 4].
* **Framework de Interface:** Python 3 com Kivy (renderização vetorial direta via canvas OpenGL)[cite: 1, 4].

### 3.3. Viabilidade Técnica da Renderização no Kivy
Para manter o consumo de recursos dentro do limite do Celeron J1900[cite: 1, 4]:
* As animações do avatar Aion não utilizarão vídeos pré-renderizados em loop ou sequências pesadas de imagens[cite: 1, 4].
* A renderização será realizada 100% via instruções de desenho vetorial do Kivy (`Color`, `Line`, `Arc`, `Mesh`, `PushMatrix`, `Rotate`)[cite: 1, 4].
* As rotações 3D e reatividades de áudio serão calculadas matematicamente via código Python, garantindo uma taxa estável de 60 FPS com baixíssimo uso de memória e CPU[cite: 1, 4].

---

## 4. Roteiro de Implementação (Fases)

### Fase 1: Base do Sistema e Quiosque (Em Andamento)
* [x] Instalação do Debian 13 minimal[cite: 1, 4].
* [x] Validação da GPU Intel integrada e driver `i915`[cite: 1, 4].
* [ ] Configuração do pacote `sudo` e inclusão do usuário `aura` ao grupo de administradores[cite: 1, 4].
* [ ] Configuração da inicialização automática em modo quiosque (`xorg` + `nodm` / `xinit` sem gerenciador de janelas)[cite: 1, 4].

### Fase 2: Protótipo do Avatar Aion (Kivy)
* [ ] Criação do script Python/Kivy para renderização da esfera central e anéis concêntricos[cite: 1, 4].
* [ ] Implementação da rotação independente por anel fracionado usando `PushMatrix` e `Rotate`[cite: 1, 4].
* [ ] Desenvolvimento da máquina de estados visuais (*Standby*, *Listening*, *Processing*, *Speaking*)[cite: 1, 4].
* [ ] Integração do módulo de reatividade de áudio (VU-meter) para variação de escala e brilho na fala[cite: 1, 4].

### Fase 3: Módulos do Smart Mirror e Periféricos
* [ ] Desenvolvimento dos widgets informativos (relógio, clima, status de sistema) em layouts periféricos[cite: 1, 4].
* [ ] Conexão Serial/USB (`pySerial`) com ESP32 para leitura de sensores de presença/distância local[cite: 1, 4].

---

## 5. Histórico de Colaboração e Contribuições

### [Claude — Metodologia e Versionamento] (30/09/2026)
* Consolidação das diretrizes de registro de autoria e padronização da nomenclatura de arquivos no formato `projeto-aura-DD.MM.AAAA-autor-HHhMM.md`[cite: 1].
* Registro da máquina de estados e inicialização em modo quiosque[cite: 1].

### [Gemini — Design do Avatar e Análise Multimídia] (04/10/2026)
* **Análise Visual de Vídeos de Referência:** Identificação dos padrões HUD Sci-Fi 3D (anéis fracionados, eixos inclinados $X, Y, Z$, marcas de calibração e núcleo esférico)[cite: 2, 3, 4].
* **Tradução Conceitual:** Definição do design não-antropomórfico (sem rosto/olhos humanos) para evitar estranhamento visual atrás do espelho[cite: 4].
* **Especificação Kivy:** Confirmação da viabilidade de renderização vetorial no canvas OpenGL do Kivy para execução fluida no Celeron J1900[cite: 1, 4].