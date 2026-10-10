"""
Projeto Aura - Aion - Esboco 06 (VU de borda + anel externo tipo dial)
------------------------------------------------------------------------
Reestrutura em camadas, do centro para fora:
  1) Nucleo (estatico - SEM a pulsacao da V05, removida por decisao)
  2) Anel VU: barras radiais coladas na borda do nucleo, representando
     audio (amplitude SIMULADA por enquanto, mesmo principio de
     ataque/decaimento da V05, agora uma por barra)
  3) Aneis de segmentos orbitando (V04, mantidos como estavam)
  4) Anel externo estatico tipo mostrador/dial (marcacoes regulares,
     sem animacao) - so para dar sensacao de profundidade/instrumento

O centro do nucleo fica vazio por enquanto - a ideia de exibir ali um
simbolo de expressao (tipo abreviacoes de texto: "?!", "kkk", etc.,
conforme o que o audio esta "dizendo") fica registrada para uma
proxima etapa, nao implementada ainda.
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

# ---- Placeholders faceis de trocar depois ----
COR_NEON = (0.1, 0.9, 1.0, 1.0)
COR_FUNDO = (0.03, 0.03, 0.05, 1)

RAIO_NUCLEO = 120

# velocidade_mag_min/max: faixa de VELOCIDADE (sem sinal, so o "quanto")
# sorteada para cada segmento. O SENTIDO (sinal) nao vem daqui - ele
# alterna automaticamente entre segmentos vizinhos (ver ALTERNAR_SENTIDO
# mais abaixo), pra evitar o efeito de "cardume" de todos andando juntos
# na mesma direcao dentro de um anel.
# raio_variacao: cada segmento sorteia seu proprio raio dentro de
# "raio" +/- "raio_variacao" - assim nenhum segmento compartilha
# exatamente a mesma trajetoria, e eles se cruzam em vez de se
# sobrepor quando um alcanca o outro.
ANEIS = [
    {"raio": 210, "largura": 3, "segmentos": 6, "velocidade_mag_min": 8,  "velocidade_mag_max": 28, "raio_variacao": 25},
    {"raio": 275, "largura": 2, "segmentos": 9, "velocidade_mag_min": 4,  "velocidade_mag_max": 20, "raio_variacao": 25},
]

# Se True, segmentos vizinhos (na ordem em que foram colocados ao redor
# do anel) giram em sentidos opostos. Se False, volta ao comportamento
# anterior (sentido fixo por anel).
ALTERNAR_SENTIDO = True

# ---- Anel VU (audio SIMULADO por enquanto) ----
VU_N_BARRAS = 28
VU_RAIO_INTERNO = 128       # onde a barra "nasce" (colada na borda do nucleo)
VU_COMPRIMENTO_MIN = 5      # comprimento da barra em silencio (nao some)
VU_COMPRIMENTO_MAX = 42     # comprimento da barra no pico
VU_LARGURA_BARRA = 3

# Ataque rapido / decaimento mais rapido que a respiracao da V05 -
# um equalizador de audio reage mais rapido que uma "respiracao".
VU_ENVELOPE_ATAQUE = 0.35
VU_ENVELOPE_DECAIMENTO = 0.08
VU_NOVO_ALVO_INTERVALO_MIN = 0.08
VU_NOVO_ALVO_INTERVALO_MAX = 0.35

# ---- Anel externo estatico (tipo mostrador/dial) ----
DIAL_RAIO = 330
DIAL_LARGURA_CIRCULO = 1.5
DIAL_N_MARCAS = 40
DIAL_MARCA_CURTA = 8
DIAL_MARCA_LONGA = 16
DIAL_A_CADA_MARCA_LONGA = 5   # uma marca longa a cada N marcas (estilo bussola)
DIAL_LARGURA_MARCA = 2

# Dentro da faixa de cada anel, o espaco (2 x raio_variacao) e dividido
# em fatias iguais - uma por segmento - e cada segmento sorteia seu
# raio DENTRO da sua propria fatia (com um pouco de folga/jitter).
# Isso evita tanto segmentos colados (fatias garantem distancia minima)
# quanto um espacamento irregular demais (nao e 100% aleatorio solto).
JITTER_FATIA = 0.3  # 0 = raio sempre no centro da fatia; 1 = pode usar a fatia toda

SEG_PESO_MIN = 0.9
SEG_PESO_MAX = 1.4
GAP_GRAUS_MIN = 4
GAP_GRAUS_MAX = 16
SEMENTE_ALEATORIA = 42


def gerar_arcos(n_seg, rng):
    """Gera (inicio, fim) de n_seg arcos com tamanhos variados e gaps
    aleatorios, distribuidos ao redor dos 360 graus do circulo."""
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
    """Divide a faixa [raio_base - variacao, raio_base + variacao] em
    n_seg fatias iguais e sorteia um raio dentro de cada fatia (com
    um pouco de jitter). Garante espacamento minimo entre orbitas
    vizinhas, em vez de deixa-las se amontoarem por puro acaso."""
    largura_fatia = (2 * variacao) / n_seg
    jitter = (largura_fatia / 2) * JITTER_FATIA
    raios = []
    for i in range(n_seg):
        centro_fatia = (raio_base - variacao) + (i + 0.5) * largura_fatia
        raios.append(centro_fatia + rng.uniform(-jitter, jitter))
    rng.shuffle(raios)  # evita correlacao entre posicao angular e raio
    return raios


class EnvelopeSimulado:
    """Gera uma amplitude simulada (0 a 1) e a suaviza com ataque
    rapido / decaimento lento (estilo medidor de VU). Usado por cada
    barra do anel de VU - cada barra tem a sua propria instancia, com
    seus proprios tempos de pico, pra nao ficarem todas sincronizadas.

    Quando o audio real existir, basta trocar `amplitude_simulada` por
    uma leitura real (ex: energia de uma faixa de frequencia); o
    metodo `atualizar` continua igual."""

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
        return self.envelope  # 0 a 1


class BarraVU:
    """Uma barra radial do anel de VU: angulo fixo, comprimento
    variavel de acordo com seu proprio envelope simulado."""

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
    """Um unico pedaco de anel: guarda sua geometria e velocidade
    proprias, e a instrucao Line que o desenha (atualizada a cada
    quadro, sem precisar redesenhar o canvas inteiro)."""

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
            # Nucleo - estatico (sem pulsacao; removida por decisao)
            Color(*COR_NEON)
            Ellipse(pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                     size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2))

            # Anel VU - colado na borda do nucleo, uma barra por angulo
            # fixo, cada uma com seu proprio envelope simulado
            rng_vu = random.Random()  # nao precisa ser reproduzivel
            passo_vu = 360 / VU_N_BARRAS
            Color(*COR_NEON)
            for i in range(VU_N_BARRAS):
                angulo = i * passo_vu
                line = Line(points=[0, 0, 0, 0], width=VU_LARGURA_BARRA)
                envelope = EnvelopeSimulado(
                    rng_vu, VU_ENVELOPE_ATAQUE, VU_ENVELOPE_DECAIMENTO,
                    VU_NOVO_ALVO_INTERVALO_MIN, VU_NOVO_ALVO_INTERVALO_MAX,
                )
                self.barras_vu.append(BarraVU(line, angulo, envelope))

            # Anel externo estatico tipo dial (circulo fino + marcacoes)
            Color(*COR_NEON)
            Line(
                ellipse=(cx - DIAL_RAIO, cy - DIAL_RAIO,
                         DIAL_RAIO * 2, DIAL_RAIO * 2),
                width=DIAL_LARGURA_CIRCULO,
            )
            for i in range(DIAL_N_MARCAS):
                angulo = radians(i * (360 / DIAL_N_MARCAS))
                eh_longa = (i % DIAL_A_CADA_MARCA_LONGA == 0)
                comprimento = DIAL_MARCA_LONGA if eh_longa else DIAL_MARCA_CURTA
                x1 = cx + cos(angulo) * DIAL_RAIO
                y1 = cy + sin(angulo) * DIAL_RAIO
                x2 = cx + cos(angulo) * (DIAL_RAIO - comprimento)
                y2 = cy + sin(angulo) * (DIAL_RAIO - comprimento)
                Line(points=[x1, y1, x2, y2], width=DIAL_LARGURA_MARCA)

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

                Color(*COR_NEON)
                for i, ((inicio, fim), raio) in enumerate(zip(arcos, raios)):
                    line = Line(
                        ellipse=(cx - raio, cy - raio, raio * 2, raio * 2,
                                 inicio, fim),
                        width=largura,
                    )
                    magnitude = rng.uniform(v_mag_min, v_mag_max)
                    if ALTERNAR_SENTIDO:
                        sinal = 1 if i % 2 == 0 else -1
                    else:
                        sinal = 1
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
        self.title = "Projeto Aura - Aion - Esboco 06"
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
