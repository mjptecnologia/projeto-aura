"""
Projeto Aura - Aion - Esboco 04 (raio proprio por segmento)
------------------------------------------------------------------------
Mesma base do esboco 03 (cada segmento com velocidade de rotacao
independente), mas agora cada segmento tambem sorteia seu PROPRIO RAIO
dentro da faixa do anel (raio +/- raio_variacao). Assim, ao se
alcancarem, os segmentos passam em trajetorias levemente diferentes em
vez de se sobreporem exatamente na mesma orbita.
"""

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '760')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
import random

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
    {"raio": 165, "largura": 3, "segmentos": 6, "velocidade_mag_min": 8,  "velocidade_mag_max": 28, "raio_variacao": 30},
    {"raio": 245, "largura": 2, "segmentos": 9, "velocidade_mag_min": 4,  "velocidade_mag_max": 20, "raio_variacao": 30},
]

# Se True, segmentos vizinhos (na ordem em que foram colocados ao redor
# do anel) giram em sentidos opostos. Se False, volta ao comportamento
# anterior (sentido fixo por anel).
ALTERNAR_SENTIDO = True

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
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def montar(self, *args):
        self.canvas.clear()
        self.segmentos = []
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            Color(*COR_NEON)
            Ellipse(pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                     size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2))

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


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 04"
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
