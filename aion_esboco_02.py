"""
Projeto Aura - Aion - Esboco 02 (rotacao dos aneis)
------------------------------------------------------
Mesma forma do esboco 01 (nucleo + 2 aneis fracionados com
segmentos de tamanho aleatorio), agora com cada anel girando
numa velocidade independente. O nucleo continua parado por
enquanto - a pulsacao entra na proxima etapa.
"""

from kivy.config import Config
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Ellipse, Line, Rectangle,
    PushMatrix, PopMatrix, Rotate,
)
import random

# ---- Placeholders faceis de trocar depois ----
COR_NEON = (0.1, 0.9, 1.0, 1.0)
COR_FUNDO = (0.03, 0.03, 0.05, 1)

RAIO_NUCLEO = 120

ANEIS = [
    {"raio": 170, "largura": 4, "segmentos": 10, "velocidade": 18},   # graus/seg
    {"raio": 220, "largura": 2, "segmentos": 16, "velocidade": -11},  # negativo = sentido contrario
]

SEG_PESO_MIN = 0.4
SEG_PESO_MAX = 1.6
GAP_GRAUS_MIN = 4
GAP_GRAUS_MAX = 16
SEMENTE_ALEATORIA = 42


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


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotates = []          # uma instrucao Rotate por anel, pra girar depois
        self.velocidades = []      # graus/seg de cada anel, na mesma ordem
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def montar(self, *args):
        """(Re)constroi todo o desenho - chamado quando o widget muda de
        tamanho/posicao (ex: redimensionar a janela)."""
        self.canvas.clear()
        self.rotates = []
        self.velocidades = []
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            # Nucleo central (parado por enquanto)
            Color(*COR_NEON)
            Ellipse(pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                     size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2))

            # Cada anel ganha seu proprio grupo de rotacao independente
            rng = random.Random(SEMENTE_ALEATORIA)
            for anel in ANEIS:
                raio = anel["raio"]
                largura = anel["largura"]
                n_seg = anel["segmentos"]

                PushMatrix()
                rotate = Rotate(angle=0, origin=(cx, cy))
                self.rotates.append(rotate)
                self.velocidades.append(anel["velocidade"])

                Color(*COR_NEON)
                for inicio, fim in gerar_arcos(n_seg, rng):
                    Line(
                        ellipse=(cx - raio, cy - raio, raio * 2, raio * 2,
                                 inicio, fim),
                        width=largura,
                    )
                PopMatrix()

    def atualizar(self, dt):
        for rotate, velocidade in zip(self.rotates, self.velocidades):
            rotate.angle = (rotate.angle + velocidade * dt) % 360


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 02"
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
