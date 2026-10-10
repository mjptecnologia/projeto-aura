"""
Projeto Aura - Aion - Esboco 03 (segmentos com rotacao independente)
------------------------------------------------------------------------
Em vez do anel inteiro girar como um bloco rigido, agora CADA SEGMENTO
gira na sua propria velocidade (dentro de uma faixa definida por anel).
Isso faz os pedacos se espalharem e se reencontrarem com o tempo, em
vez de girarem sempre juntos. Nucleo continua parado por enquanto.
"""

from kivy.config import Config
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '720')
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

# velocidade_min/max: faixa de graus/seg sorteada PARA CADA SEGMENTO
# (numeros negativos giram no sentido contrario)
ANEIS = [
    {"raio": 170, "largura": 4, "segmentos": 10, "velocidade_min": 8,  "velocidade_max": 28},
    {"raio": 220, "largura": 2, "segmentos": 16, "velocidade_min": -20, "velocidade_max": -4},
]

SEG_PESO_MIN = 0.4
SEG_PESO_MAX = 1.6
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
                raio = anel["raio"]
                largura = anel["largura"]
                n_seg = anel["segmentos"]
                v_min = anel["velocidade_min"]
                v_max = anel["velocidade_max"]

                Color(*COR_NEON)
                for inicio, fim in gerar_arcos(n_seg, rng):
                    line = Line(
                        ellipse=(cx - raio, cy - raio, raio * 2, raio * 2,
                                 inicio, fim),
                        width=largura,
                    )
                    velocidade = rng.uniform(v_min, v_max)
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
        self.title = "Projeto Aura - Aion - Esboco 03"
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
