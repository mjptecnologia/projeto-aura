"""
Projeto Aura - Aion - Esboco 07 (salto de refinamento visual)
------------------------------------------------------------------------
Mesma estrutura em camadas da V06 (nucleo, VU de borda, segmentos
orbitando da V04, anel externo tipo dial), mas com um salto grande de
acabamento, usando so truques 2D (sem motor 3D, sem imagens externas):

  - Nucleo com gradiente simulado (camadas de circulos deslocados) para
    parecer uma esfera de luz, com um "brilho" (highlight) sugerindo
    uma fonte de luz vindo de cima-esquerda.
  - Glow em camadas atras do nucleo, das barras de VU e dos segmentos
    orbitando (linha larga e transparente por baixo da linha nitida).
  - Pontas arredondadas (cap='round') em todas as linhas, para um
    acabamento mais suave, menos "serrilhado".
  - Achatamento vertical leve (elipse em vez de circulo perfeito) no
    VU, nos aneis de segmentos e no dial - sugere um disco visto
    ligeiramente de cima, sem precisar de calculo 3D de verdade.
  - Paleta com mais de um tom (nucleo, brilho, cor principal, cor do
    glow, cor do dial mais apagada) em vez de uma unica cor neon plana
    repetida em tudo.
"""

from kivy.config import Config
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
import random
from math import cos, sin, radians

# ======================================================================
# PALETA - varios tons em vez de uma cor neon plana unica
# ======================================================================
COR_FUNDO = (0.012, 0.016, 0.035, 1)        # quase preto, leve tom azulado

COR_NUCLEO_BASE = (0.03, 0.22, 0.42, 1)     # azul profundo (base da "esfera")
COR_NUCLEO_BRILHO = (0.68, 0.96, 1.0, 1)    # quase branco-ciano (highlight)

COR_PRINCIPAL = (0.15, 0.85, 1.0, 1)        # ciano neon - VU e segmentos
COR_GLOW = (0.25, 0.85, 1.0, 1)             # mesma familia, usada so em baixa opacidade

COR_DIAL = (0.30, 0.55, 0.68, 0.55)         # mais apagada - fica ao fundo

# Direcao simulada da luz sobre o nucleo (fracao do raio)
LUZ_DX = -0.32
LUZ_DY = 0.32

# Achatamento vertical (perspectiva simulada) aplicado ao VU, aos
# segmentos e ao dial. O nucleo fica 1.0 (circulo perfeito, de frente).
ESCALA_Y = 0.88

RAIO_NUCLEO = 120

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
VU_N_BARRAS = 28
VU_RAIO_INTERNO = 128
VU_COMPRIMENTO_MIN = 5
VU_COMPRIMENTO_MAX = 42
VU_LARGURA_BARRA = 3
VU_ENVELOPE_ATAQUE = 0.35
VU_ENVELOPE_DECAIMENTO = 0.08
VU_NOVO_ALVO_INTERVALO_MIN = 0.08
VU_NOVO_ALVO_INTERVALO_MAX = 0.35

# ---- Anel externo estatico (dial) ----
DIAL_RAIO = 330
DIAL_LARGURA_CIRCULO = 1.4
DIAL_N_MARCAS = 40
DIAL_MARCA_CURTA = 8
DIAL_MARCA_LONGA = 16
DIAL_A_CADA_MARCA_LONGA = 5
DIAL_LARGURA_MARCA = 1.6

# ---- Glow (halo) ----
GLOW_LARGURA_MULT = 3.4   # quanto mais larga a linha de glow vs a linha nitida
GLOW_ALPHA = 0.16         # opacidade da linha de glow

GLOW_NUCLEO_CAMADAS = 4
GLOW_NUCLEO_RAIO_MAX_MULT = 1.4
GLOW_NUCLEO_ALPHA_BASE = 0.10


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
    """Uma barra radial do anel de VU, com uma linha de glow (larga e
    transparente) por baixo da linha nitida principal."""

    def __init__(self, line_glow, line, angulo_graus, envelope):
        self.line_glow = line_glow
        self.line = line
        self.angulo = radians(angulo_graus)
        self.envelope = envelope
        self.cos_a = cos(self.angulo)
        self.sin_a = sin(self.angulo) * ESCALA_Y

    def atualizar(self, dt, cx, cy):
        nivel = self.envelope.atualizar(dt)
        comprimento = VU_COMPRIMENTO_MIN + nivel * (VU_COMPRIMENTO_MAX - VU_COMPRIMENTO_MIN)
        x1 = cx + self.cos_a * VU_RAIO_INTERNO
        y1 = cy + self.sin_a * VU_RAIO_INTERNO
        x2 = cx + self.cos_a * (VU_RAIO_INTERNO + comprimento)
        y2 = cy + self.sin_a * (VU_RAIO_INTERNO + comprimento)
        pontos = [x1, y1, x2, y2]
        self.line.points = pontos
        self.line_glow.points = pontos


class Segmento:
    """Um pedaco de anel: raio, velocidade e visual (linha nitida +
    linha de glow) proprios."""

    def __init__(self, line_glow, line, raio, inicio, fim, velocidade):
        self.line_glow = line_glow
        self.line = line
        self.raio = raio
        self.inicio = inicio
        self.fim = fim
        self.velocidade = velocidade
        self.deslocamento = 0.0

    def atualizar(self, dt, cx, cy):
        self.deslocamento = (self.deslocamento + self.velocidade * dt) % 360
        params = (
            cx - self.raio, cy - self.raio * ESCALA_Y,
            self.raio * 2, self.raio * 2 * ESCALA_Y,
            self.inicio + self.deslocamento,
            self.fim + self.deslocamento,
        )
        self.line.ellipse = params
        self.line_glow.ellipse = params


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segmentos = []
        self.barras_vu = []
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def montar(self, *args):
        self.canvas.clear()
        self.segmentos = []
        self.barras_vu = []
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            # ---- glow externo do nucleo (camadas crescentes, bem fracas) ----
            for i in range(GLOW_NUCLEO_CAMADAS, 0, -1):
                t = i / GLOW_NUCLEO_CAMADAS
                raio_glow = RAIO_NUCLEO * (1 + (GLOW_NUCLEO_RAIO_MAX_MULT - 1) * t)
                Color(COR_GLOW[0], COR_GLOW[1], COR_GLOW[2],
                      GLOW_NUCLEO_ALPHA_BASE * (1 - t + 0.15))
                Ellipse(pos=(cx - raio_glow, cy - raio_glow),
                         size=(raio_glow * 2, raio_glow * 2))

            # ---- nucleo: base solida + camadas de brilho deslocadas ----
            Color(*COR_NUCLEO_BASE)
            Ellipse(pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                     size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2))

            n_camadas_brilho = 6
            for i in range(n_camadas_brilho):
                t = i / (n_camadas_brilho - 1)  # 0 (borda) -> 1 (centro do brilho)
                raio_camada = RAIO_NUCLEO * (0.92 - 0.62 * t)
                offset_x = LUZ_DX * RAIO_NUCLEO * 0.45 * t
                offset_y = LUZ_DY * RAIO_NUCLEO * 0.45 * t
                cor = [
                    COR_NUCLEO_BASE[k] + (COR_NUCLEO_BRILHO[k] - COR_NUCLEO_BASE[k]) * t
                    for k in range(3)
                ]
                Color(cor[0], cor[1], cor[2], 0.22)
                Ellipse(
                    pos=(cx + offset_x - raio_camada, cy + offset_y - raio_camada),
                    size=(raio_camada * 2, raio_camada * 2),
                )

            # ---- anel de VU (glow + linha nitida, por barra) ----
            rng_vu = random.Random()
            passo_vu = 360 / VU_N_BARRAS
            for i in range(VU_N_BARRAS):
                angulo = i * passo_vu
                Color(COR_GLOW[0], COR_GLOW[1], COR_GLOW[2], GLOW_ALPHA)
                line_glow = Line(points=[0, 0, 0, 0],
                                   width=VU_LARGURA_BARRA * GLOW_LARGURA_MULT,
                                   cap='round')
                Color(*COR_PRINCIPAL)
                line = Line(points=[0, 0, 0, 0], width=VU_LARGURA_BARRA, cap='round')
                envelope = EnvelopeSimulado(
                    rng_vu, VU_ENVELOPE_ATAQUE, VU_ENVELOPE_DECAIMENTO,
                    VU_NOVO_ALVO_INTERVALO_MIN, VU_NOVO_ALVO_INTERVALO_MAX,
                )
                self.barras_vu.append(BarraVU(line_glow, line, angulo, envelope))

            # ---- anel externo estatico tipo dial (achatado, apagado) ----
            Color(*COR_DIAL)
            Line(
                ellipse=(cx - DIAL_RAIO, cy - DIAL_RAIO * ESCALA_Y,
                         DIAL_RAIO * 2, DIAL_RAIO * 2 * ESCALA_Y),
                width=DIAL_LARGURA_CIRCULO,
            )
            for i in range(DIAL_N_MARCAS):
                angulo = radians(i * (360 / DIAL_N_MARCAS))
                eh_longa = (i % DIAL_A_CADA_MARCA_LONGA == 0)
                comprimento = DIAL_MARCA_LONGA if eh_longa else DIAL_MARCA_CURTA
                ca, sa = cos(angulo), sin(angulo) * ESCALA_Y
                x1 = cx + ca * DIAL_RAIO
                y1 = cy + sa * DIAL_RAIO
                x2 = cx + ca * (DIAL_RAIO - comprimento)
                y2 = cy + sa * (DIAL_RAIO - comprimento)
                Line(points=[x1, y1, x2, y2], width=DIAL_LARGURA_MARCA, cap='round')

            # ---- aneis de segmentos orbitando (glow + linha nitida) ----
            rng = random.Random(SEMENTE_ALEATORIA)
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
                    Color(COR_GLOW[0], COR_GLOW[1], COR_GLOW[2], GLOW_ALPHA)
                    line_glow = Line(
                        ellipse=(cx - raio, cy - raio * ESCALA_Y,
                                 raio * 2, raio * 2 * ESCALA_Y, inicio, fim),
                        width=largura * GLOW_LARGURA_MULT,
                        cap='round',
                    )
                    Color(*COR_PRINCIPAL)
                    line = Line(
                        ellipse=(cx - raio, cy - raio * ESCALA_Y,
                                 raio * 2, raio * 2 * ESCALA_Y, inicio, fim),
                        width=largura,
                        cap='round',
                    )
                    magnitude = rng.uniform(v_mag_min, v_mag_max)
                    sinal = 1 if (ALTERNAR_SENTIDO and i % 2 == 0) else (-1 if ALTERNAR_SENTIDO else 1)
                    velocidade = sinal * magnitude
                    self.segmentos.append(
                        Segmento(line_glow, line, raio, inicio, fim, velocidade)
                    )

    def atualizar(self, dt):
        cx = self.center_x
        cy = self.center_y
        for seg in self.segmentos:
            seg.atualizar(dt, cx, cy)
        for barra in self.barras_vu:
            barra.atualizar(dt, cx, cy)


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 07"
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
