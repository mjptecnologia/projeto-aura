"""
Projeto Aura - Aion - Esboco 08 (correcoes sobre a V07)
------------------------------------------------------------------------
Ajustes pedidos em cima da V07:

  - REMOVIDO o efeito de glow (linha larga/transparente por baixo da
    linha nitida) - ficou com aparencia ruim. Linhas voltam a ser so
    a versao nitida, uma unica vez.
  - REMOVIDO o achatamento eliptico (ESCALA_Y volta a 1.0) - tudo que
    e circunferencia (VU, segmentos, dial) volta a ser um circulo de
    verdade, sem distorcao.
  - Anel de VU com MUITO mais tracos (140, mais finos cada um).
  - Nucleo agora usa uma TEXTURA COM GRADIENTE RADIAL DE VERDADE
    (gerada em codigo, sem numpy/PIL - so Python puro + Kivy Texture),
    claro na borda e escurecendo suavemente ate o centro - a ideia de
    "boca de buraco de minhoca" pedida, em vez do efeito de camadas
    empilhadas da V07 (que parecia deformado).
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

# ---- Gradiente do nucleo (textura gerada em codigo, gradiente real) ----
# "Boca de buraco de minhoca": claro na borda, escurece suavemente
# rumo ao centro. TAMANHO_TEXTURA e a resolucao da textura gerada -
# nao precisa ser grande, ela e esticada ao tamanho do nucleo na tela.
NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)   # tom proximo ao do VU/segmentos
NUCLEO_GRAD_CENTRO = (0.015, 0.03, 0.05, 1)  # quase preto
NUCLEO_GRAD_GAMA = 0.55   # <1 = escurece mais rapido perto do centro
TAMANHO_TEXTURA_NUCLEO = 128


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


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segmentos = []
        self.barras_vu = []
        # gerada uma unica vez - independe do tamanho da janela
        self.textura_nucleo = criar_textura_radial(
            TAMANHO_TEXTURA_NUCLEO, NUCLEO_GRAD_CENTRO, NUCLEO_GRAD_BORDA,
            NUCLEO_GRAD_GAMA,
        )
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
            # ---- nucleo: textura com gradiente radial real ----
            Color(1, 1, 1, 1)  # branco para nao tingir a textura
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
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

            # ---- anel externo estatico tipo dial (circulo de verdade) ----
            Color(*COR_DIAL)
            Line(
                ellipse=(cx - DIAL_RAIO, cy - DIAL_RAIO,
                         DIAL_RAIO * 2, DIAL_RAIO * 2),
                width=DIAL_LARGURA_CIRCULO,
            )
            for i in range(DIAL_N_MARCAS):
                angulo = radians(i * (360 / DIAL_N_MARCAS))
                eh_longa = (i % DIAL_A_CADA_MARCA_LONGA == 0)
                comprimento = DIAL_MARCA_LONGA if eh_longa else DIAL_MARCA_CURTA
                ca, sa = cos(angulo), sin(angulo)
                x1 = cx + ca * DIAL_RAIO
                y1 = cy + sa * DIAL_RAIO
                x2 = cx + ca * (DIAL_RAIO - comprimento)
                y2 = cy + sa * (DIAL_RAIO - comprimento)
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


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 08"
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
