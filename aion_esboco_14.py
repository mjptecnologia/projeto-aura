"""
Projeto Aura - Aion - Esboco 14 (tamanho dobrado + audio real)
------------------------------------------------------------------------
Sobre a V13 (nucleo com degradue + onda senoidal simulada):

  - Tamanho geral dobrado (nucleo, espessura da onda, janela).
  - A onda agora pode reagir a AUDIO DE VERDADE captado pelo
    microfone: o som e analisado (FFT) e dividido em 3 bandas
    (graves/medios/agudos), cada uma controlando um componente
    diferente da onda - funciona como um analisador de espectro
    simples. Precisa de "pip install sounddevice numpy".
  - Se as bibliotecas nao estiverem instaladas, ou o microfone nao
    puder ser aberto, o app cai sozinho de volta para a simulacao
    (nao trava) - ver USAR_AUDIO_REAL e AUDIO_LIBS_OK.
"""

from kivy.config import Config
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from math import sin
import random

# ======================================================================
# Audio real (opcional) - precisa de: pip install sounddevice numpy
# Se nao estiver instalado, ou se o microfone nao puder ser aberto, o
# app cai sozinho de volta para a simulacao (nao trava).
# ======================================================================
try:
    import numpy as np
    import sounddevice as sd
    AUDIO_LIBS_OK = True
except ImportError:
    AUDIO_LIBS_OK = False

USAR_AUDIO_REAL = True   # mude para False para forcar o modo simulado

SAMPLERATE = 44100
BLOCKSIZE = 1024
# faixas de frequencia aproximadas: graves, medios, agudos (em Hz)
BANDAS_FAIXAS_HZ = [(20, 250), (250, 2000), (2000, 8000)]

# ======================================================================
# Nucleo - degradue interno (mesma tecnica ja aprovada antes)
# ======================================================================
COR_FUNDO = (0.0, 0.0, 0.0, 1)   # preto solido (sem sutileza - ver nota do vidro)

RAIO_NUCLEO = 280   # dobrado (era 140)

NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)    # tom claro, na borda
NUCLEO_GRAD_CENTRO = (0.0, 0.0, 0.0, 1)      # preto solido no centro
NUCLEO_GRAD_GAMA = 4.0     # fica escuro por mais tempo, so clareia perto da borda
TAMANHO_TEXTURA_NUCLEO = 128

# ======================================================================
# Onda senoidal - representa as frequencias da fala (amplitude SIMULADA)
# ======================================================================
ONDA_COR = (1.0, 1.0, 1.0, 1.0)     # branco solido - maxima visibilidade atras do vidro
ONDA_LARGURA = 6                    # dobrado (era 3)
ONDA_N_PONTOS = 48
ONDA_LARGURA_AREA = RAIO_NUCLEO * 1.6   # extensao horizontal do desenho da onda
ONDA_AMPLITUDE_MAX = RAIO_NUCLEO * 0.55
ONDA_AMPLITUDE_MINIMA_REPOUSO = 0.06    # fracao da amplitude maxima, mesmo "em silencio"

# Cada componente da onda agora e ligada a uma "banda" de frequencia do
# audio real (0 = graves, 1 = medios, 2 = agudos) - ver CapturadorAudio
# mais abaixo. peso_max e o quanto cada uma pode contribuir no pico;
# os pesos somam 1.0, entao a onda nunca passa de ONDA_AMPLITUDE_MAX.
ONDA_COMPONENTES = [
    # (frequencia_visual, peso_max, indice_da_banda)
    (1.0, 0.5, 0),   # graves
    (2.3, 0.3, 1),   # medios
    (4.1, 0.2, 2),   # agudos
]
ONDA_VELOCIDADE_FASE = 2.6   # velocidade do "fluir" da onda (rad/seg)

# Envelope simulado (mesmo principio de ataque/decaimento das versoes
# anteriores) controlando o quanto a onda "fala" a cada momento.
ENVELOPE_ATAQUE = 0.18
ENVELOPE_DECAIMENTO = 0.05
ENVELOPE_INTERVALO_MIN = 0.5
ENVELOPE_INTERVALO_MAX = 1.6


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
            t = d ** gama
            idx = (y * tamanho + x) * 4
            buf[idx + 0] = int((cor_centro[0] + (cor_borda[0] - cor_centro[0]) * t) * 255)
            buf[idx + 1] = int((cor_centro[1] + (cor_borda[1] - cor_centro[1]) * t) * 255)
            buf[idx + 2] = int((cor_centro[2] + (cor_borda[2] - cor_centro[2]) * t) * 255)
            buf[idx + 3] = 255
    textura.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    return textura


class EnvelopeSimulado:
    """Amplitude simulada (0 a 1), suavizada com ataque rapido /
    decaimento mais lento. Representa, por enquanto, uma simulacao de
    atividade de fala - no futuro e so trocar a origem do numero por
    volume de audio real; a logica de suavizacao continua igual."""

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


class CapturadorAudio:
    """Captura o microfone padrao em tempo real e calcula, a cada
    bloco de audio: o nivel geral (RMS) e a energia em 3 bandas de
    frequencia (graves/medios/agudos), cada uma normalizada pelo seu
    proprio pico recente (assim funciona em qualquer volume, sem
    precisar calibrar nada manualmente).

    A captura roda numa thread separada (e do proprio sounddevice);
    aqui so guardamos numeros simples (float), lidos pelo Kivy a cada
    quadro - seguro o suficiente para este uso (nao exige lock)."""

    def __init__(self):
        self.nivel = 0.0
        self.bandas = [0.0, 0.0, 0.0]
        self._pico_nivel = 0.01
        self._pico_bandas = [0.01, 0.01, 0.01]
        self._janela = np.hanning(BLOCKSIZE)
        freqs = np.fft.rfftfreq(BLOCKSIZE, 1 / SAMPLERATE)
        self._mascaras = [
            (freqs >= f0) & (freqs < f1) for f0, f1 in BANDAS_FAIXAS_HZ
        ]
        self.stream = sd.InputStream(
            channels=1, samplerate=SAMPLERATE, blocksize=BLOCKSIZE,
            callback=self._callback,
        )
        self.stream.start()

    def _callback(self, indata, frames, time_info, status):
        amostra = indata[:, 0]
        rms = float(np.sqrt(np.mean(amostra ** 2)) + 1e-9)
        # o "pico" decai bem devagar com o tempo - e o que permite
        # normalizar sem precisar de um numero fixo de calibracao
        self._pico_nivel = max(self._pico_nivel * 0.999, rms)
        self.nivel = min(1.0, rms / self._pico_nivel)

        espectro = np.abs(np.fft.rfft(amostra * self._janela))
        for i, mascara in enumerate(self._mascaras):
            valor = float(espectro[mascara].mean()) if mascara.any() else 0.0
            self._pico_bandas[i] = max(self._pico_bandas[i] * 0.999, valor, 1e-6)
            self.bandas[i] = min(1.0, valor / self._pico_bandas[i])

    def parar(self):
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass


def suavizar(atual, alvo, ataque, decaimento):
    coef = ataque if alvo > atual else decaimento
    return atual + (alvo - atual) * coef


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.textura_nucleo = criar_textura_radial(
            TAMANHO_TEXTURA_NUCLEO, NUCLEO_GRAD_CENTRO, NUCLEO_GRAD_BORDA,
            NUCLEO_GRAD_GAMA,
        )
        # tenta abrir o audio real; se nao der (sem libs, sem
        # microfone, sem permissao...), cai para a simulacao sozinho
        self.capturador = None
        if AUDIO_LIBS_OK and USAR_AUDIO_REAL:
            try:
                self.capturador = CapturadorAudio()
                print("Aion: usando audio real do microfone.")
            except Exception as erro:
                print(f"Aion: nao consegui abrir o audio real ({erro}); "
                      f"usando simulacao.")
        else:
            print("Aion: audio real desligado ou bibliotecas ausentes "
                  "(pip install sounddevice numpy); usando simulacao.")

        self.envelope = EnvelopeSimulado(
            random.Random(), ENVELOPE_ATAQUE, ENVELOPE_DECAIMENTO,
            ENVELOPE_INTERVALO_MIN, ENVELOPE_INTERVALO_MAX,
        )
        self.bandas_suaves = [0.0, 0.0, 0.0]
        self.fase = 0.0
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def montar(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            Color(1, 1, 1, 1)  # branco para nao tingir a textura
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
            )
            Color(*ONDA_COR)
            self.linha_onda = Line(points=[0, 0, 0, 0], width=ONDA_LARGURA, cap='round')

    def atualizar(self, dt):
        cx = self.center_x
        cy = self.center_y
        self.fase += dt * ONDA_VELOCIDADE_FASE

        if self.capturador is not None:
            # audio real: cada banda (grave/medio/agudo) e suavizada
            # com o mesmo principio de ataque/decaimento de antes
            alvos_banda = self.capturador.bandas
        else:
            # simulacao: todas as bandas seguem o mesmo envelope
            nivel_simulado = self.envelope.atualizar(dt)
            alvos_banda = [nivel_simulado, nivel_simulado, nivel_simulado]

        for i in range(3):
            self.bandas_suaves[i] = suavizar(
                self.bandas_suaves[i], alvos_banda[i],
                ENVELOPE_ATAQUE, ENVELOPE_DECAIMENTO,
            )

        pontos = []
        for i in range(ONDA_N_PONTOS):
            t = i / (ONDA_N_PONTOS - 1)          # 0..1
            x_rel = (t - 0.5) * ONDA_LARGURA_AREA  # -metade..+metade
            y_rel = 0.0
            for freq, peso_max, indice_banda in ONDA_COMPONENTES:
                nivel_banda = self.bandas_suaves[indice_banda]
                nivel_efetivo = (
                    ONDA_AMPLITUDE_MINIMA_REPOUSO
                    + (1 - ONDA_AMPLITUDE_MINIMA_REPOUSO) * nivel_banda
                )
                y_rel += peso_max * nivel_efetivo * sin(freq * (t * 6.2832) + self.fase)
            y_rel *= ONDA_AMPLITUDE_MAX
            pontos.append(cx + x_rel)
            pontos.append(cy + y_rel)

        self.linha_onda.points = pontos


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 14"
        root = Widget()

        with root.canvas.before:
            Color(*COR_FUNDO)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._atualizar_fundo, size=self._atualizar_fundo)

        self.nucleo = NucleoAion()
        self.nucleo.size = root.size
        self.nucleo.pos = root.pos
        root.bind(pos=lambda w, v: setattr(self.nucleo, 'pos', v))
        root.bind(size=lambda w, v: setattr(self.nucleo, 'size', v))
        root.add_widget(self.nucleo)
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def on_stop(self):
        if self.nucleo.capturador is not None:
            self.nucleo.capturador.parar()


if __name__ == "__main__":
    AionApp().run()
