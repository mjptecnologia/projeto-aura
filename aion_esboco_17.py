"""
Projeto Aura - Aion - Esboco 17 (osciloscopio / eletrocardiograma)
------------------------------------------------------------------------
Em vez de um grafico de frequencias (V15/V16), o nucleo agora mostra a
AMPLITUDE DO AUDIO AO LONGO DO TEMPO, como um osciloscopio ou o papel
de um eletrocardiograma: uma unica linha fina e solida, que vai sendo
desenhada e CAMINHA sem parar. Sem audio, a linha fica reta, mas segue
"andando" (o papel nao para).

  - A "caneta" (o momento atual) fica em OSC_POSICAO_AGORA:
        0.5 = no centro do nucleo (padrao)
        1.0 = na borda direita (osciloscopio classico em "roll")
  - O historico caminha para o lado de OSC_SENTIDO ("esquerda"/"direita").
  - O trecho a frente da caneta (ainda "nao escrito") e uma linha reta
    na altura do eixo (OSC_RETA_A_FRENTE).
  - A velocidade e OSC_JANELA_SEG: quantos segundos cabem na largura
    inteira da linha (menor = anda mais rapido).

Audio do proprio PC (loopback do Windows), antes do volume do sistema:
    pip install PyAudioWPatch numpy
Se nao houver audio real e PERMITIR_SIMULACAO = False, a linha fica
reta (sem movimento falso). O titulo da janela mostra a fonte do audio.
"""

from kivy.config import Config
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from collections import deque
import random
import time

# ======================================================================
# Audio real (opcional) - precisa de: pip install PyAudioWPatch numpy
# ======================================================================
try:
    import numpy as np
    import pyaudiowpatch as pyaudio
    AUDIO_LIBS_OK = True
except ImportError:
    AUDIO_LIBS_OK = False

# "loopback" = audio que o PC esta tocando | "microfone" | "simulado"
ORIGEM_AUDIO = "loopback"
MICROFONE_COMO_RESERVA = True      # se o loopback falhar, tenta o microfone
PERMITIR_SIMULACAO = False         # False = nunca inventa movimento
BLOCKSIZE = 1024                   # quadros por bloco de audio (~21 ms a 48 kHz)
SEM_AUDIO_APOS = 0.25              # s sem blocos de audio => silencio

# ======================================================================
# Visual
# ======================================================================
COR_FUNDO = (0.0, 0.0, 0.0, 1)
RAIO_NUCLEO = 280
NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)
NUCLEO_GRAD_CENTRO = (0.0, 0.0, 0.0, 1)
NUCLEO_GRAD_GAMA = 4.0
TAMANHO_TEXTURA_NUCLEO = 128

ONDA_COR = (1.0, 1.0, 1.0, 1.0)    # solida (alpha 1), por causa do vidro
ONDA_LARGURA = 2                   # (3) fina
ONDA_LARGURA_AREA = RAIO_NUCLEO * 1.7   # largura total do tracado
ONDA_AMPLITUDE_MAX = RAIO_NUCLEO * 0.25

# ---- Osciloscopio ----
OSC_JANELA_SEG = 6.0         # (3.0) segundos que cabem na largura inteira
OSC_COLUNAS = 150            # (240) resolucao horizontal (mais = mais detalhe)
OSC_POSICAO_AGORA = 1.0      # 0..1 - onde fica o "agora" (0.5 centro, 1.0 borda)
OSC_SENTIDO = "esquerda"     # para onde o historico caminha
OSC_RETA_A_FRENTE = True     # linha reta no trecho ainda "nao escrito"

# Ganho / ruido (amplitude relativa ao fundo de escala)
PISO_RUIDO_OSC = 0.004       # picos abaixo disso viram zero (linha reta)
PISO_PICO_OSC = 0.02         # pico minimo assumido (nao amplifica ruido)
PICO_MEIA_VIDA = 5.0         # s para o ganho "esquecer" um som alto
CURVA_DINAMICA = 4.0         # (0.7) <1 realca detalhes fracos (1 = linear)


# ======================================================================
# Logica do osciloscopio (so numpy, sem Kivy - testavel sozinha)
# ======================================================================
class Osciloscopio:
    """Mantem as colunas do tracado (valores -1..1; o mais novo e o
    ultimo da fila). Cada coluna representa dt_col segundos e e o pico
    COM SINAL da fatia de audio daquele intervalo (assim a linha oscila
    para cima e para baixo como um osciloscopio/ECG)."""

    def __init__(self, samplerate, n_historico):
        self.dt_col = OSC_JANELA_SEG / OSC_COLUNAS
        self.slice_n = max(1, int(round(samplerate * self.dt_col))) if samplerate else 1
        self.colunas = deque([0.0] * n_historico, maxlen=n_historico)
        self.resto = np.zeros(0, dtype=np.float32) if AUDIO_LIBS_OK else None
        self.pico = PISO_PICO_OSC
        self.decaimento_col = 0.5 ** (self.dt_col / PICO_MEIA_VIDA)
        self.acum = 0.0

    def _normalizar(self, v):
        self.pico = max(self.pico * self.decaimento_col, abs(v), PISO_PICO_OSC)
        x = max(-1.0, min(1.0, v / self.pico))
        return (abs(x) ** CURVA_DINAMICA) * (1 if x >= 0 else -1)

    def alimentar(self, bloco):
        """Recebe audio real (mono, float -1..1) e gera as colunas."""
        self.resto = np.concatenate((self.resto, bloco)) if len(self.resto) else bloco
        n = self.slice_n
        total = len(self.resto) // n
        for i in range(total):
            fatia = self.resto[i * n:(i + 1) * n]
            v = float(fatia[int(np.argmax(np.abs(fatia)))])
            if abs(v) < PISO_RUIDO_OSC:
                v = 0.0
            self.colunas.append(self._normalizar(v))
        self.resto = self.resto[total * n:]

    def avancar_sem_audio(self, dt):
        """O 'papel' continua andando: colunas zeradas, pelo relogio."""
        self.acum += dt
        while self.acum >= self.dt_col:
            self.acum -= self.dt_col
            self.colunas.append(self._normalizar(0.0))

    def avancar_simulado(self, dt, fala, rng):
        self.acum += dt
        while self.acum >= self.dt_col:
            self.acum -= self.dt_col
            nivel = fala.atualizar(self.dt_col)
            self.colunas.append(nivel * rng.uniform(-1.0, 1.0))


# ======================================================================
# Captura de audio (loopback do PC / microfone)
# ======================================================================
class CapturadorAudio:
    """Abre o audio e guarda os blocos (mono) numa fila; quem le e o
    Kivy, a cada quadro. deque.append/popleft sao seguros entre threads."""

    def __init__(self, origem):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.fila = deque(maxlen=64)
        self.ultimo_bloco = 0.0
        self.origem = origem
        self.nome = ""
        self.samplerate = 0
        try:
            info = self._escolher_dispositivo(origem)
            self.canais = max(1, int(info["maxInputChannels"]))
            self.samplerate = int(info["defaultSampleRate"])
            self.nome = info["name"]
            self.stream = self.pa.open(
                format=pyaudio.paInt16, channels=self.canais,
                rate=self.samplerate, frames_per_buffer=BLOCKSIZE, input=True,
                input_device_index=int(info["index"]),
                stream_callback=self._callback,
            )
            self.stream.start_stream()
        except Exception:
            self.parar()
            raise

    def _escolher_dispositivo(self, origem):
        if origem == "loopback":
            wasapi = self.pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            saida = self.pa.get_device_info_by_index(wasapi["defaultOutputDevice"])
            if saida.get("isLoopbackDevice", False):
                return saida
            for loop in self.pa.get_loopback_device_info_generator():
                if saida["name"] in loop["name"]:
                    return loop
            raise RuntimeError("nao achei o loopback da saida de audio padrao")
        return self.pa.get_default_input_device_info()

    def _callback(self, in_data, frame_count, time_info, status):
        try:
            dados = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            if self.canais > 1:
                dados = dados.reshape(-1, self.canais).mean(axis=1)
            self.fila.append(dados)
            self.ultimo_bloco = time.monotonic()
        except Exception:
            pass
        return (None, pyaudio.paContinue)

    def parar(self):
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass
        try:
            self.pa.terminate()
        except Exception:
            pass


# ======================================================================
# Simulacao (so se PERMITIR_SIMULACAO = True)
# ======================================================================
class EnvelopeSimulado:
    def __init__(self, rng, ataque, decaimento, intervalo_min, intervalo_max):
        self.rng = rng
        self.ataque = ataque
        self.decaimento = decaimento
        self.intervalo_min = intervalo_min
        self.intervalo_max = intervalo_max
        self.envelope = 0.0
        self.alvo = 0.0
        self.tempo = rng.uniform(0, intervalo_max)

    def atualizar(self, dt):
        self.tempo -= dt
        if self.tempo <= 0:
            self.alvo = self.rng.uniform(0.0, 1.0)
            self.tempo = self.rng.uniform(self.intervalo_min, self.intervalo_max)
        coef = self.ataque if self.alvo > self.envelope else self.decaimento
        self.envelope += (self.alvo - self.envelope) * coef
        return self.envelope


def criar_textura_radial(tamanho, cor_centro, cor_borda, gama):
    """Gradiente radial suave (escuro no centro, claro na borda)."""
    textura = Texture.create(size=(tamanho, tamanho), colorfmt='rgba')
    buf = bytearray(tamanho * tamanho * 4)
    centro = (tamanho - 1) / 2
    for y in range(tamanho):
        for x in range(tamanho):
            dx = (x - centro) / centro
            dy = (y - centro) / centro
            d = min(1.0, (dx * dx + dy * dy) ** 0.5)
            t = d ** gama
            idx = (y * tamanho + x) * 4
            for c in range(3):
                buf[idx + c] = int((cor_centro[c] + (cor_borda[c] - cor_centro[c]) * t) * 255)
            buf[idx + 3] = 255
    textura.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    return textura


class NucleoAion(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.textura_nucleo = criar_textura_radial(
            TAMANHO_TEXTURA_NUCLEO, NUCLEO_GRAD_CENTRO, NUCLEO_GRAD_BORDA,
            NUCLEO_GRAD_GAMA,
        )
        self.status_audio = ""
        self.capturador = self._abrir_audio()

        # quantas colunas ficam "atras" da caneta (o historico visivel)
        frac_hist = OSC_POSICAO_AGORA if OSC_SENTIDO == "esquerda" else 1 - OSC_POSICAO_AGORA
        self.n_hist = max(2, int(round(frac_hist * OSC_COLUNAS)))
        taxa = self.capturador.samplerate if self.capturador else 0
        self.osc = Osciloscopio(taxa, self.n_hist)

        self.simulacao = None
        if self.capturador is None and PERMITIR_SIMULACAO:
            rng = random.Random()
            self.simulacao = (EnvelopeSimulado(rng, 0.25, 0.08, 0.6, 1.8), rng)
            self.status_audio = "SIMULACAO (audio falso)"
        elif self.capturador is None:
            self.status_audio = "SEM AUDIO (veja o console)"
            print("Aion: sem audio real e simulacao desligada "
                  "(PERMITIR_SIMULACAO = False): a linha fica reta.")

        self.linha = None
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def _abrir_audio(self):
        if ORIGEM_AUDIO == "simulado":
            print("Aion: ORIGEM_AUDIO = 'simulado'.")
            return None
        if not AUDIO_LIBS_OK:
            print("Aion: faltam bibliotecas -> pip install PyAudioWPatch numpy")
            return None
        tentativas = [ORIGEM_AUDIO]
        if ORIGEM_AUDIO == "loopback" and MICROFONE_COMO_RESERVA:
            tentativas.append("microfone")
        for origem in tentativas:
            try:
                cap = CapturadorAudio(origem)
                self.status_audio = f"audio real: {origem} - {cap.nome}"
                print(f"Aion: {self.status_audio}")
                return cap
            except Exception as erro:
                print(f"Aion: nao consegui abrir '{origem}' ({erro}).")
        return None

    def montar(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        with self.canvas:
            Color(1, 1, 1, 1)
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
            )
            Color(*ONDA_COR)
            self.linha = Line(points=[0, 0, 0, 0], width=ONDA_LARGURA,
                              cap='round', joint='round')

    def _avancar(self, dt):
        """Faz o 'papel' andar: audio real, silencio ou simulacao."""
        if self.capturador is not None:
            recebeu = False
            while self.capturador.fila:
                self.osc.alimentar(self.capturador.fila.popleft())
                recebeu = True
            if not recebeu and (time.monotonic() - self.capturador.ultimo_bloco
                                > SEM_AUDIO_APOS):
                self.osc.avancar_sem_audio(dt)      # silencio: papel anda, linha reta
        elif self.simulacao is not None:
            fala, rng = self.simulacao
            self.osc.avancar_simulado(dt, fala, rng)
        else:
            self.osc.avancar_sem_audio(dt)

    def atualizar(self, dt):
        self._avancar(dt)
        cx = self.center_x
        cy = self.center_y
        sentido = -1 if OSC_SENTIDO == "esquerda" else 1
        dx = ONDA_LARGURA_AREA / OSC_COLUNAS
        x_caneta = cx + (OSC_POSICAO_AGORA - 0.5) * ONDA_LARGURA_AREA

        # do mais novo (na caneta) ao mais antigo (na ponta do historico)
        novo_para_antigo = list(self.osc.colunas)[::-1]
        pontos = []
        if OSC_RETA_A_FRENTE:
            comprimento_frente = (1 - OSC_POSICAO_AGORA if sentido == -1
                                  else OSC_POSICAO_AGORA) * ONDA_LARGURA_AREA
            pontos += [x_caneta - sentido * comprimento_frente, cy, x_caneta, cy]
        for k, v in enumerate(novo_para_antigo):
            pontos.append(x_caneta + sentido * k * dx)
            pontos.append(cy + v * ONDA_AMPLITUDE_MAX)
        self.linha.points = pontos


class AionApp(App):
    def build(self):
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

        self.title = f"Aion V17 [osciloscopio] | {self.nucleo.status_audio}"
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def on_stop(self):
        if self.nucleo.capturador is not None:
            self.nucleo.capturador.parar()


if __name__ == "__main__":
    AionApp().run()
