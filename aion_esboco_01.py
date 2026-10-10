"""
Projeto Aura - Aion - Esboco 01 (forma estatica)
--------------------------------------------------
Nucleo central + aneis fracionados (segmentados) ao redor.
Sem rotacao, sem pulsacao: so para validar silhueta e proporcoes.

Cor e tamanho de janela sao placeholders faceis de ajustar
(ver as constantes logo abaixo).
"""

from kivy.config import Config
# Janela em proporcao retrato: metade do tamanho real do monitor
# HP w1907 girado (900x1440). Ajuste aqui quando for testar em outra tela.
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
import random

# ---- Placeholders faceis de trocar depois ----
COR_NEON = (0.1, 0.9, 1.0, 1.0)   # ciano neon (R, G, B, A) - escolha definitiva em aberto
COR_FUNDO = (0.03, 0.03, 0.05, 1)  # quase preto, realca o neon

RAIO_NUCLEO = 120            # raio do circulo central, em pixels (dobrado)

# Duas camadas de aneis, cada uma com segmentos de tamanho aleatorio
ANEIS = [
    {"raio": 170, "largura": 4, "segmentos": 10},
    {"raio": 220, "largura": 2, "segmentos": 16},
]

# Faixas de variacao aleatoria (em "peso" relativo, nao graus fixos)
SEG_PESO_MIN = 0.4   # segmento mais curto possivel (relativo)
SEG_PESO_MAX = 1.6   # segmento mais longo possivel (relativo)
GAP_GRAUS_MIN = 4    # espaco vazio minimo entre segmentos, em graus
GAP_GRAUS_MAX = 16   # espaco vazio maximo entre segmentos, em graus

# Fixa a aleatoriedade para o visual nao mudar a cada execucao.
# Troque o numero para gerar uma distribuicao diferente dos segmentos.
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
    angulo = rng.uniform(0, 360)  # rotacao inicial aleatoria do padrao
    for tamanho, gap in zip(tamanhos_segmentos, gaps):
        inicio = angulo
        fim = angulo + tamanho
        arcos.append((inicio, fim))
        angulo = fim + gap
    return arcos


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redesenhar, size=self.redesenhar)
        self.redesenhar()

    def redesenhar(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            # Nucleo central (circulo solido)
            Color(*COR_NEON)
            Ellipse(pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                     size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2))

            # Aneis fracionados (segmentados), um por configuracao em ANEIS,
            # com tamanho de cada pedaco variando aleatoriamente.
            rng = random.Random(SEMENTE_ALEATORIA)
            for anel in ANEIS:
                raio = anel["raio"]
                largura = anel["largura"]
                n_seg = anel["segmentos"]
                Color(*COR_NEON)
                for inicio, fim in gerar_arcos(n_seg, rng):
                    Line(
                        ellipse=(cx - raio, cy - raio, raio * 2, raio * 2,
                                 inicio, fim),
                        width=largura,
                    )


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 01"
        root = Widget()
        with root.canvas.before:
            Color(*COR_FUNDO)
            self._bg = Ellipse()  # placeholder, substituido abaixo por um retangulo
        from kivy.graphics import Rectangle
        root.canvas.before.clear()
        with root.canvas.before:
            Color(*COR_FUNDO)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._atualizar_fundo, size=self._atualizar_fundo)

        nucleo = NucleoAion()
        root.add_widget(nucleo)
        nucleo.size = root.size
        nucleo.pos = root.pos
        root.bind(pos=lambda w, v: setattr(nucleo, 'pos', v))
        root.bind(size=lambda w, v: setattr(nucleo, 'size', v))
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size


if __name__ == "__main__":
    AionApp().run()
