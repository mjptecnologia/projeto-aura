"""
Projeto Aura - Aion - Esboco 11 (corpo mais visivel + digitos + faixa dupla)
------------------------------------------------------------------------
Ajustes sobre a V10:

  - Gradiente de "corpo" bem mais visivel (cor mais clara, zona clara
    mais larga) - na V10 estava quase imperceptivel no notebook.
  - O globo giratorio foi SUBSTITUIDO por um efeito "buraco de
    minhoca": digitos "0" e "1" nascem perto da borda do nucleo e
    caminham devagar ate o centro, encolhendo pelo caminho - sensacao
    de profundidade/movimento para dentro, lento. Implementado com
    texto renderizado uma unica vez como textura (CoreLabel), depois
    so reposicionado/redimensionado a cada quadro - bem leve.
  - Faixa externa mais larga, agora com DUAS linhas perimetrais
    (externa e interna), nao so uma - fica com cara de moldura/faixa
    de verdade, nao so um limite solto.
"""

from kivy.config import Config
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.text import Label as CoreLabel
import random
from math import cos, sin, radians

# ======================================================================
# PALETA - varios tons em vez de uma cor neon plana unica
# ======================================================================
COR_FUNDO = (0.012, 0.016, 0.035, 1)        # quase preto, leve tom azulado

COR_PRINCIPAL = (0.15, 0.85, 1.0, 1)        # ciano neon - VU e segmentos
COR_DIAL = (0.30, 0.55, 0.68, 0.55)         # mais apagada - fica ao fundo

# Achatamento vertical - DESATIVADO por decisao (ficou com aparencia
# deformada). Mantido como constante, em 1.0, para nao precisar reescrever
# todos os calculos que a usam - 1.0 = circulo perfeito, sem achatamento.
ESCALA_Y = 1.0

RAIO_NUCLEO = 120

# ---- "Buraco de minhoca" de digitos binarios no centro do nucleo ----
# Substitui o globo: digitos "0" e "1" nascem perto da borda do
# nucleo e vao encolhendo e caminhando para o centro, devagar, dando
# sensacao de profundidade/movimento para dentro (tipo um tunel).
DIGITOS_RAIO_MAX = RAIO_NUCLEO * 0.92   # onde o digito "nasce"
DIGITOS_RAIO_MIN = 6                    # onde ele "desaparece" (bem no centro)
DIGITOS_N = 34
DIGITOS_TAMANHO_MAX = 15   # tamanho (px) ao nascer, na borda
DIGITOS_TAMANHO_MIN = 4    # tamanho ao chegar perto do centro
DIGITOS_COR = (0.55, 0.88, 0.92, 0.85)
DIGITOS_FONTE_BASE = 40    # resolucao do texto gerado (nao precisa mudar)
DIGITOS_DURACAO_MIN = 4.0  # segundos para atravessar da borda ao centro
DIGITOS_DURACAO_MAX = 8.0  # (lento, como pedido)

ANEIS = [
    {"raio": 210, "largura": 3, "segmentos": 6, "velocidade_mag_min": 8,  "velocidade_mag_max": 28, "raio_variacao": 25},
    {"raio": 275, "largura": 2, "segmentos": 9, "velocidade_mag_min": 4,  "velocidade_mag_max": 20, "raio_variacao": 25},
]

SEG_PESO_MIN = 0.9
SEG_PESO_MAX = 1.4
GAP_GRAUS_MIN = 4
GAP_GRAUS_MAX = 16
SEMENTE_ALEATORIA = 42
JITTER_FATIA = 0.3
ALTERNAR_SENTIDO = True

# ---- Anel VU ----
VU_N_BARRAS = 140           # bem mais traços, mais fino cada um
VU_RAIO_INTERNO = 128
VU_COMPRIMENTO_MIN = 5
VU_COMPRIMENTO_MAX = 42
VU_LARGURA_BARRA = 1.6
VU_ENVELOPE_ATAQUE = 0.12          # era 0.35 - reacao mais lenta, menos nervosa
VU_ENVELOPE_DECAIMENTO = 0.035     # era 0.08
VU_NOVO_ALVO_INTERVALO_MIN = 0.6   # era 0.08 - novos "picos" bem menos frequentes
VU_NOVO_ALVO_INTERVALO_MAX = 1.8   # era 0.35

# ---- Anel externo estatico: faixa larga com tracinhos uniformes e
# proximos, dando um limite com "textura" em vez de uma linha solta ----
DIAL_RAIO = 330
DIAL_LARGURA_CIRCULO = 1.4
DIAL_N_MARCAS = 180          # bem mais denso e uniforme (era 40, com marcas longa/curta)
DIAL_MARCA_COMPRIMENTO = 22  # faixa mais larga (era 10)
DIAL_LARGURA_MARCA = 1.6

# ---- Gradiente do nucleo (textura gerada em codigo, gradiente real) ----
# "Boca de buraco de minhoca": claro na borda, escurece suavemente
# rumo ao centro. TAMANHO_TEXTURA e a resolucao da textura gerada -
# nao precisa ser grande, ela e esticada ao tamanho do nucleo na tela.
NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)   # tom proximo ao do VU/segmentos
NUCLEO_GRAD_CENTRO = (0.015, 0.03, 0.05, 1)  # quase preto
# >1 = fica escuro por mais tempo, so clareia mesmo perto da borda
# (valor antigo, 0.55, fazia o azul "subir" rapido demais rumo ao centro)
NUCLEO_GRAD_GAMA = 4.0
TAMANHO_TEXTURA_NUCLEO = 128


# ---- Gradiente de "corpo" (fundo, atras de tudo) ----
# Da volume/estrutura ao conjunto (fica visivel como um halo em volta
# do nucleo, ja que o nucleo e desenhado por cima, cobrindo o centro).
# Tambem e o "gradiente vivo": respira lentamente, mudando aos poucos
# a curva do gradiente - textura bem definida (mesma tecnica do
# nucleo), nao e um efeito de glow/blur.
CORPO_RAIO = 300
CORPO_COR_CENTRO = (0.20, 0.68, 0.75, 1)   # bem mais visivel que antes (era 0.10/0.30/0.38)
CORPO_COR_BORDA = (0.012, 0.02, 0.035, 1)  # se funde no fundo da tela
CORPO_GAMA_MIN = 2.8   # mais alto = zona clara mais larga antes de escurecer
CORPO_GAMA_MAX = 5.0
CORPO_VELOCIDADE_RESPIRACAO = 0.10   # ciclos lentos (quanto menor, mais lento)
CORPO_INTERVALO_ATUALIZACAO = 0.2    # regenera a textura no maximo 5x/seg (leve)
TAMANHO_TEXTURA_CORPO = 128

# ---- Raios estruturais (decoracao estatica, do globo ate a borda) ----
RAIOS_N = 8
RAIOS_COR = (0.2, 0.55, 0.65, 0.35)   # escurecido, discreto
RAIOS_LARGURA = 5
RAIOS_RAIO_INTERNO_MULT = 1.15        # comeca um pouco depois da borda do globo


def criar_textura_radial(tamanho, cor_centro, cor_borda, gama):
    """Gera uma textura quadrada com gradiente radial suave (circular),
    clara na borda e escura no centro. Pura Python/Kivy, sem numpy."""
    textura = Texture.create(size=(tamanho, tamanho), colorfmt='rgba')
    buf = bytearray(tamanho * tamanho * 4)
    centro = (tamanho - 1) / 2
    raio_max = centro
    for y in range(tamanho):
        for x in range(tamanho):
            dx = (x - centro) / raio_max
            dy = (y - centro) / raio_max
            d = min(1.0, (dx * dx + dy * dy) ** 0.5)
            t = d ** gama  # 0 no centro, 1 na borda
            idx = (y * tamanho + x) * 4
            buf[idx + 0] = int((cor_centro[0] + (cor_borda[0] - cor_centro[0]) * t) * 255)
            buf[idx + 1] = int((cor_centro[1] + (cor_borda[1] - cor_centro[1]) * t) * 255)
            buf[idx + 2] = int((cor_centro[2] + (cor_borda[2] - cor_centro[2]) * t) * 255)
            buf[idx + 3] = 255
    textura.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    return textura


def gerar_arcos(n_seg, rng):
    gaps = [rng.uniform(GAP_GRAUS_MIN, GAP_GRAUS_MAX) for _ in range(n_seg)]
    pesos = [rng.uniform(SEG_PESO_MIN, SEG_PESO_MAX) for _ in range(n_seg)]
    graus_disponiveis = 360 - sum(gaps)
    soma_pesos = sum(pesos)
    tamanhos_segmentos = [p / soma_pesos * graus_disponiveis for p in pesos]
    arcos = []
    angulo = rng.uniform(0, 360)
    for tamanho, gap in zip(tamanhos_segmentos, gaps):
        inicio = angulo
        fim = angulo + tamanho
        arcos.append((inicio, fim))
        angulo = fim + gap
    return arcos


def gerar_raios(n_seg, raio_base, variacao, rng):
    largura_fatia = (2 * variacao) / n_seg
    jitter = (largura_fatia / 2) * JITTER_FATIA
    raios = []
    for i in range(n_seg):
        centro_fatia = (raio_base - variacao) + (i + 0.5) * largura_fatia
        raios.append(centro_fatia + rng.uniform(-jitter, jitter))
    rng.shuffle(raios)
    return raios


class EnvelopeSimulado:
    """Amplitude simulada (0 a 1), suavizada com ataque rapido /
    decaimento mais lento. Trocar `amplitude-alvo` por audio real no
    futuro nao muda a logica de suavizacao."""

    def __init__(self, rng, ataque, decaimento, intervalo_min, intervalo_max):
        self.rng = rng
        self.ataque = ataque
        self.decaimento = decaimento
        self.intervalo_min = intervalo_min
        self.intervalo_max = intervalo_max
        self.envelope = 0.0
        self.alvo_simulado = 0.0
        self.tempo_para_novo_alvo = rng.uniform(0, intervalo_max)

    def atualizar(self, dt):
        self.tempo_para_novo_alvo -= dt
        if self.tempo_para_novo_alvo <= 0:
            self.alvo_simulado = self.rng.uniform(0.0, 1.0)
            self.tempo_para_novo_alvo = self.rng.uniform(
                self.intervalo_min, self.intervalo_max
            )
        coef = self.ataque if self.alvo_simulado > self.envelope else self.decaimento
        self.envelope += (self.alvo_simulado - self.envelope) * coef
        return self.envelope


class BarraVU:
    """Uma barra radial do anel de VU."""

    def __init__(self, line, angulo_graus, envelope):
        self.line = line
        self.angulo = radians(angulo_graus)
        self.envelope = envelope
        self.cos_a = cos(self.angulo)
        self.sin_a = sin(self.angulo)

    def atualizar(self, dt, cx, cy):
        nivel = self.envelope.atualizar(dt)
        comprimento = VU_COMPRIMENTO_MIN + nivel * (VU_COMPRIMENTO_MAX - VU_COMPRIMENTO_MIN)
        x1 = cx + self.cos_a * VU_RAIO_INTERNO
        y1 = cy + self.sin_a * VU_RAIO_INTERNO
        x2 = cx + self.cos_a * (VU_RAIO_INTERNO + comprimento)
        y2 = cy + self.sin_a * (VU_RAIO_INTERNO + comprimento)
        self.line.points = [x1, y1, x2, y2]


class Segmento:
    """Um pedaco de anel: raio, velocidade e visual proprios."""

    def __init__(self, line, raio, inicio, fim, velocidade):
        self.line = line
        self.raio = raio
        self.inicio = inicio
        self.fim = fim
        self.velocidade = velocidade
        self.deslocamento = 0.0

    def atualizar(self, dt, cx, cy):
        self.deslocamento = (self.deslocamento + self.velocidade * dt) % 360
        self.line.ellipse = (
            cx - self.raio, cy - self.raio,
            self.raio * 2, self.raio * 2,
            self.inicio + self.deslocamento,
            self.fim + self.deslocamento,
        )


def criar_textura_digito(caractere):
    """Renderiza um caractere ('0' ou '1') uma unica vez, em branco
    (sem cor propria), para ser reaproveitado como textura - a cor de
    verdade e aplicada depois, no Color() que vem antes do Rectangle
    que desenha cada particula."""
    rotulo = CoreLabel(text=caractere, font_size=DIGITOS_FONTE_BASE, bold=True)
    rotulo.refresh()
    return rotulo.texture


class DigitoBinario:
    """Uma particula "0" ou "1" que nasce perto da borda do nucleo e
    caminha devagar ate o centro, encolhendo pelo caminho - de longe
    em longe, reinicia em um novo angulo aleatorio."""

    def __init__(self, rect, texturas, rng):
        self.rect = rect
        self.texturas = texturas
        self.rng = rng
        self.reiniciar()

    def reiniciar(self):
        self.angulo = radians(self.rng.uniform(0, 360))
        self.duracao = self.rng.uniform(DIGITOS_DURACAO_MIN, DIGITOS_DURACAO_MAX)
        self.tempo = 0.0
        self.rect.texture = self.rng.choice(self.texturas)

    def atualizar(self, dt, cx, cy):
        self.tempo += dt
        progresso = self.tempo / self.duracao
        if progresso >= 1.0:
            self.reiniciar()
            progresso = 0.0

        raio = DIGITOS_RAIO_MAX - (DIGITOS_RAIO_MAX - DIGITOS_RAIO_MIN) * progresso
        tamanho = DIGITOS_TAMANHO_MAX - (DIGITOS_TAMANHO_MAX - DIGITOS_TAMANHO_MIN) * progresso

        x = cx + cos(self.angulo) * raio
        y = cy + sin(self.angulo) * raio
        self.rect.pos = (x - tamanho / 2, y - tamanho / 2)
        self.rect.size = (tamanho, tamanho)


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segmentos = []
        self.barras_vu = []
        self.digitos = []
        # texturas dos digitos - geradas uma unica vez, reaproveitadas
        # por todas as particulas (so a posicao/tamanho/cor mudam)
        self.texturas_digitos = [
            criar_textura_digito('0'), criar_textura_digito('1'),
        ]
        # gerada uma unica vez - independe do tamanho da janela
        self.textura_nucleo = criar_textura_radial(
            TAMANHO_TEXTURA_NUCLEO, NUCLEO_GRAD_CENTRO, NUCLEO_GRAD_BORDA,
            NUCLEO_GRAD_GAMA,
        )
        # textura do corpo: comeca com uma gama qualquer, e re-gerada
        # periodicamente em atualizar() para "respirar"
        self.textura_corpo = criar_textura_radial(
            TAMANHO_TEXTURA_CORPO, CORPO_COR_CENTRO, CORPO_COR_BORDA,
            CORPO_GAMA_MIN,
        )
        self._fase_respiracao = 0.0
        self._tempo_para_atualizar_corpo = 0.0
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def montar(self, *args):
        self.canvas.clear()
        self.segmentos = []
        self.barras_vu = []
        self.digitos = []
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            # ---- corpo: gradiente de fundo grande (atras de tudo) ----
            Color(1, 1, 1, 1)
            self.corpo_ellipse = Ellipse(
                pos=(cx - CORPO_RAIO, cy - CORPO_RAIO),
                size=(CORPO_RAIO * 2, CORPO_RAIO * 2),
                texture=self.textura_corpo,
            )

            # ---- raios estruturais (decoracao estatica) ----
            Color(*RAIOS_COR)
            raio_interno_raios = RAIO_NUCLEO * RAIOS_RAIO_INTERNO_MULT
            for i in range(RAIOS_N):
                angulo = radians(i * (360 / RAIOS_N))
                ca, sa = cos(angulo), sin(angulo)
                x1 = cx + ca * raio_interno_raios
                y1 = cy + sa * raio_interno_raios
                x2 = cx + ca * CORPO_RAIO
                y2 = cy + sa * CORPO_RAIO
                Line(points=[x1, y1, x2, y2], width=RAIOS_LARGURA, cap='round')

            # ---- nucleo: textura com gradiente radial real ----
            Color(1, 1, 1, 1)  # branco para nao tingir a textura
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
            )

            # ---- buraco de minhoca de digitos binarios, no centro ----
            rng_digitos = random.Random()
            Color(*DIGITOS_COR)
            for _ in range(DIGITOS_N):
                rect = Rectangle(pos=(cx, cy), size=(0, 0),
                                   texture=self.texturas_digitos[0])
                self.digitos.append(
                    DigitoBinario(rect, self.texturas_digitos, rng_digitos)
                )

            # ---- anel de VU (muitos tracos finos) ----
            rng_vu = random.Random()
            passo_vu = 360 / VU_N_BARRAS
            Color(*COR_PRINCIPAL)
            for i in range(VU_N_BARRAS):
                angulo = i * passo_vu
                line = Line(points=[0, 0, 0, 0], width=VU_LARGURA_BARRA, cap='round')
                envelope = EnvelopeSimulado(
                    rng_vu, VU_ENVELOPE_ATAQUE, VU_ENVELOPE_DECAIMENTO,
                    VU_NOVO_ALVO_INTERVALO_MIN, VU_NOVO_ALVO_INTERVALO_MAX,
                )
                self.barras_vu.append(BarraVU(line, angulo, envelope))

            # ---- anel externo estatico tipo dial (faixa: linha externa
            # + linha interna, com os tracinhos preenchendo entre elas) ----
            Color(*COR_DIAL)
            Line(
                ellipse=(cx - DIAL_RAIO, cy - DIAL_RAIO,
                         DIAL_RAIO * 2, DIAL_RAIO * 2),
                width=DIAL_LARGURA_CIRCULO,
            )
            raio_interno_faixa = DIAL_RAIO - DIAL_MARCA_COMPRIMENTO
            Line(
                ellipse=(cx - raio_interno_faixa, cy - raio_interno_faixa,
                         raio_interno_faixa * 2, raio_interno_faixa * 2),
                width=DIAL_LARGURA_CIRCULO,
            )
            for i in range(DIAL_N_MARCAS):
                angulo = radians(i * (360 / DIAL_N_MARCAS))
                ca, sa = cos(angulo), sin(angulo)
                x1 = cx + ca * DIAL_RAIO
                y1 = cy + sa * DIAL_RAIO
                x2 = cx + ca * (DIAL_RAIO - DIAL_MARCA_COMPRIMENTO)
                y2 = cy + sa * (DIAL_RAIO - DIAL_MARCA_COMPRIMENTO)
                Line(points=[x1, y1, x2, y2], width=DIAL_LARGURA_MARCA, cap='round')

            # ---- aneis de segmentos orbitando (circulos de verdade) ----
            rng = random.Random(SEMENTE_ALEATORIA)
            Color(*COR_PRINCIPAL)
            for anel in ANEIS:
                raio_base = anel["raio"]
                largura = anel["largura"]
                n_seg = anel["segmentos"]
                v_mag_min = anel["velocidade_mag_min"]
                v_mag_max = anel["velocidade_mag_max"]
                variacao = anel["raio_variacao"]

                arcos = gerar_arcos(n_seg, rng)
                raios = gerar_raios(n_seg, raio_base, variacao, rng)

                for i, ((inicio, fim), raio) in enumerate(zip(arcos, raios)):
                    line = Line(
                        ellipse=(cx - raio, cy - raio, raio * 2, raio * 2, inicio, fim),
                        width=largura,
                        cap='round',
                    )
                    magnitude = rng.uniform(v_mag_min, v_mag_max)
                    sinal = 1 if (ALTERNAR_SENTIDO and i % 2 == 0) else (-1 if ALTERNAR_SENTIDO else 1)
                    velocidade = sinal * magnitude
                    self.segmentos.append(
                        Segmento(line, raio, inicio, fim, velocidade)
                    )

    def atualizar(self, dt):
        cx = self.center_x
        cy = self.center_y
        for seg in self.segmentos:
            seg.atualizar(dt, cx, cy)
        for barra in self.barras_vu:
            barra.atualizar(dt, cx, cy)
        for digito in self.digitos:
            digito.atualizar(dt, cx, cy)

        # "Respiracao" do gradiente de corpo - fase acumula todo quadro
        # (calculo barato), mas a textura so e regerada de vez em
        # quando (calculo um pouco mais caro, nao precisa ser por
        # quadro: o movimento e lento mesmo).
        self._fase_respiracao += dt * CORPO_VELOCIDADE_RESPIRACAO
        self._tempo_para_atualizar_corpo -= dt
        if self._tempo_para_atualizar_corpo <= 0:
            self._tempo_para_atualizar_corpo = CORPO_INTERVALO_ATUALIZACAO
            # oscila suavemente entre CORPO_GAMA_MIN e CORPO_GAMA_MAX
            t = (sin(self._fase_respiracao * 6.2832) + 1) / 2  # 0..1
            gama_atual = CORPO_GAMA_MIN + (CORPO_GAMA_MAX - CORPO_GAMA_MIN) * t
            self.textura_corpo = criar_textura_radial(
                TAMANHO_TEXTURA_CORPO, CORPO_COR_CENTRO, CORPO_COR_BORDA,
                gama_atual,
            )
            self.corpo_ellipse.texture = self.textura_corpo


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 11"
        root = Widget()

        with root.canvas.before:
            Color(*COR_FUNDO)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._atualizar_fundo, size=self._atualizar_fundo)

        nucleo = NucleoAion()
        nucleo.size = root.size
        nucleo.pos = root.pos
        root.bind(pos=lambda w, v: setattr(nucleo, 'pos', v))
        root.bind(size=lambda w, v: setattr(nucleo, 'size', v))
        root.add_widget(nucleo)
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size


if __name__ == "__main__":
    AionApp().run()
