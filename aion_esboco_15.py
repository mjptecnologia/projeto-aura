"""
Projeto Aura - Aion - Esboco 15 (espectro real, 3 linhas, audio do PC)
------------------------------------------------------------------------
Sobre a V14 (nucleo com degradue + onda que reage ao audio):

  1) AUDIO DO PROPRIO PC (loopback): em vez do microfone, captura o que
     o computador esta reproduzindo (musica, video...), via WASAPI
     loopback. Pelo padrao do Windows isso e capturado ANTES do volume
     do sistema, entao mexer no volume nao deveria mudar o desenho
     (depende do dispositivo - ver explicacao no chat). Precisa de:
         pip install PyAudioWPatch numpy
     Se nao der, tenta o microfone; se nao der, cai na simulacao.

  2) ANALISADOR DE ESPECTRO DE VERDADE: sem a ondulacao lenta que
     existia sem relacao com o sinal. O desenho agora so se move
     quando ha audio; sem audio, fica reto. Cada ponto da linha e a
     energia real de uma faixa de frequencia (esquerda = grave,
     direita = agudo dentro da faixa de cada linha). Resposta mais
     rapida (ver RESPOSTA_ATAQUE / RESPOSTA_DECAIMENTO).

  3) Linha mais fina (ONDA_LARGURA).

  4) TRES LINHAS sobrepostas, cada uma cobrindo uma faixa de
     frequencia diferente (graves, medios, agudos), em cores solidas
     diferentes (sem transparencia, por causa do vidro espelhado).

Controle de ganho: cada linha se normaliza pelo proprio pico recente,
entao funciona em qualquer nivel de volume sem calibrar; um piso de
ruido evita que ruido de fundo vire desenho.
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
import random
import time

# ======================================================================
# Audio real (opcional) - precisa de: pip install PyAudioWPatch numpy
# Se faltar algo, o app NAO trava: cai para o proximo modo disponivel.
# ======================================================================
try:
    import numpy as np
    import pyaudiowpatch as pyaudio
    AUDIO_LIBS_OK = True
except ImportError:
    AUDIO_LIBS_OK = False

# "loopback" = audio que o PC esta tocando | "microfone" | "simulado"
ORIGEM_AUDIO = "loopback"
# Se o loopback falhar, tenta o microfone antes de simular?
MICROFONE_COMO_RESERVA = True

BLOCKSIZE = 1024        # quadros de audio por bloco (~21 ms a 48 kHz)
TAMANHO_FFT = 4096      # janela da analise: maior = mais resolucao nos graves

# ======================================================================
# Visual
# ======================================================================
COR_FUNDO = (0.0, 0.0, 0.0, 1)

RAIO_NUCLEO = 280
NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)
NUCLEO_GRAD_CENTRO = (0.0, 0.0, 0.0, 1)
NUCLEO_GRAD_GAMA = 4.0
TAMANHO_TEXTURA_NUCLEO = 128

# Tres linhas de espectro sobrepostas. Cada uma cobre uma faixa de
# frequencia (Hz); dentro dela, esquerda = mais grave, direita = mais
# agudo. Cores SOLIDAS (alpha 1).
ONDA_LINHAS = [
    {"faixa_hz": (20, 250),    "cor": (1.0, 1.0, 1.0, 1.0)},     # graves  - branco
    {"faixa_hz": (250, 2000),  "cor": (0.2, 0.95, 1.0, 1.0)},    # medios  - ciano
    {"faixa_hz": (2000, 8000), "cor": (0.45, 1.0, 0.75, 1.0)},   # agudos  - verde-agua
]
ONDA_LARGURA = 2            # espessura (era 6) - mais fina
ONDA_N_PONTOS = 64          # resolucao horizontal de cada linha
ONDA_LARGURA_AREA = RAIO_NUCLEO * 1.6
ONDA_AMPLITUDE_MAX = RAIO_NUCLEO * 0.55
# True: pontos alternam acima/abaixo do eixo (visual de "forma de onda"
# simetrica). False: curva so para cima, estilo grafico de espectro.
ONDA_ESPELHAR = True

# Resposta do desenho (aplicada a cada quadro, 60x/seg): mais alto =
# mais rapido. A V14 usava 0.18 / 0.05 (subida ~200 ms, queda ~750 ms).
# Com 0.45 / 0.15: subida ~70 ms, queda ~230 ms.
RESPOSTA_ATAQUE = 0.45
RESPOSTA_DECAIMENTO = 0.15

# Controle de ganho / ruido (em amplitude relativa ao fundo de escala)
PISO_RUIDO = 0.0005        # abaixo disso vira zero (desenho reto)
PISO_PICO = 0.004          # pico minimo assumido (evita amplificar ruido)
PICO_MEIA_VIDA = 5.0       # segundos para o pico "esquecer" um som alto
CURVA_DINAMICA = 0.6       # <1 realca detalhes fracos (1 = linear)

SEM_AUDIO_APOS = 0.25      # s sem blocos de audio => trata como silencio


# ======================================================================
# Analise de espectro (so numpy - sem Kivy, portanto testavel sozinha)
# ======================================================================
class AnalisadorEspectro:
    """Recebe blocos de audio mono (float -1..1) e produz, para cada
    linha, uma lista de n_pontos valores 0..1 (energia por faixa de
    frequencia, em escala logaritmica de frequencia)."""

    def __init__(self, samplerate, faixas_hz, n_pontos):
        self.samplerate = samplerate
        self.n = TAMANHO_FFT
        self.buffer = np.zeros(self.n, dtype=np.float32)
        self.janela = np.hanning(self.n).astype(np.float32)
        # amplitude de uma senoide = 2 * |FFT| / soma(janela)
        self.escala = 2.0 / float(self.janela.sum())
        largura_bin = samplerate / self.n
        n_bins = self.n // 2 + 1

        self.faixas = []
        for f_ini, f_fim in faixas_hz:
            bordas = np.geomspace(f_ini, f_fim, n_pontos + 1)
            i0 = np.floor(bordas[:-1] / largura_bin).astype(int)
            i1 = np.ceil(bordas[1:] / largura_bin).astype(int)
            i1 = np.maximum(i1, i0 + 2)            # ao menos 2 bins por ponto
            i1 = np.minimum(i1, n_bins)
            i0 = np.minimum(i0, i1 - 1)
            self.faixas.append((i0.tolist(), i1.tolist()))

        self.picos = [PISO_PICO] * len(faixas_hz)
        self.valores = [[0.0] * n_pontos for _ in faixas_hz]

    def processar(self, mono):
        m = len(mono)
        if m >= self.n:
            self.buffer[:] = mono[-self.n:]
        else:
            self.buffer[:-m] = self.buffer[m:]
            self.buffer[-m:] = mono

        espectro = np.abs(np.fft.rfft(self.buffer * self.janela)) * self.escala
        decaimento = 0.5 ** ((m / self.samplerate) / PICO_MEIA_VIDA)

        novos = []
        for k, (i0, i1) in enumerate(self.faixas):
            mags = np.array([espectro[a:b].max() for a, b in zip(i0, i1)])
            self.picos[k] = max(self.picos[k] * decaimento, float(mags.max()), PISO_PICO)
            norm = (mags - PISO_RUIDO) / (self.picos[k] - PISO_RUIDO)
            norm = np.clip(norm, 0.0, 1.0) ** CURVA_DINAMICA
            novos.append(norm.tolist())
        self.valores = novos          # troca de referencia: seguro entre threads


# ======================================================================
# Captura de audio (loopback do PC / microfone)
# ======================================================================
class CapturadorAudio:
    """Abre o audio (loopback das caixas padrao ou microfone) e alimenta
    o analisador. Roda numa thread propria (do PyAudio); o Kivy so le
    `analisador.valores` e `ultimo_bloco`."""

    def __init__(self, origem):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.analisador = None
        self.ultimo_bloco = 0.0
        self.origem = origem
        self.nome = ""
        try:
            info = self._escolher_dispositivo(origem)
            self.canais = max(1, int(info["maxInputChannels"]))
            taxa = int(info["defaultSampleRate"])
            self.nome = info["name"]
            self.analisador = AnalisadorEspectro(
                taxa, [l["faixa_hz"] for l in ONDA_LINHAS], ONDA_N_PONTOS,
            )
            self.stream = self.pa.open(
                format=pyaudio.paInt16, channels=self.canais, rate=taxa,
                frames_per_buffer=BLOCKSIZE, input=True,
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
            self.analisador.processar(dados)
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
# Simulacao (reserva - sem numpy, para rodar ate no celular)
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


class SimuladorEspectro:
    """Espectro falso, so para ver o visual quando nao ha audio real:
    uma 'atividade de fala' global modula pontos independentes."""

    def __init__(self, n_linhas, n_pontos):
        rng = random.Random()
        self.fala = EnvelopeSimulado(rng, 0.25, 0.08, 0.6, 1.8)
        self.pontos = [
            [EnvelopeSimulado(rng, 0.4, 0.15, 0.08, 0.35) for _ in range(n_pontos)]
            for _ in range(n_linhas)
        ]

    def atualizar(self, dt):
        g = self.fala.atualizar(dt)
        return [[g * p.atualizar(dt) for p in linha] for linha in self.pontos]


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
        self.capturador = self._abrir_audio()
        self.simulador = None
        if self.capturador is None:
            self.simulador = SimuladorEspectro(len(ONDA_LINHAS), ONDA_N_PONTOS)

        self.suavizados = [[0.0] * ONDA_N_PONTOS for _ in ONDA_LINHAS]
        self.linhas = []
        self.bind(pos=self.montar, size=self.montar)
        self.montar()
        Clock.schedule_interval(self.atualizar, 1 / 60)

    def _abrir_audio(self):
        if ORIGEM_AUDIO == "simulado":
            print("Aion: modo simulado (ORIGEM_AUDIO = 'simulado').")
            return None
        if not AUDIO_LIBS_OK:
            print("Aion: faltam bibliotecas (pip install PyAudioWPatch numpy); "
                  "usando simulacao.")
            return None
        tentativas = [ORIGEM_AUDIO]
        if ORIGEM_AUDIO == "loopback" and MICROFONE_COMO_RESERVA:
            tentativas.append("microfone")
        for origem in tentativas:
            try:
                cap = CapturadorAudio(origem)
                print(f"Aion: audio ativo -> {origem}: {cap.nome}")
                return cap
            except Exception as erro:
                print(f"Aion: nao consegui abrir '{origem}' ({erro}).")
        print("Aion: usando simulacao.")
        return None

    def montar(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        self.linhas = []
        with self.canvas:
            Color(1, 1, 1, 1)
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
            )
            for cfg in ONDA_LINHAS:
                Color(*cfg["cor"])
                self.linhas.append(
                    Line(points=[0, 0, 0, 0], width=ONDA_LARGURA,
                         cap='round', joint='round')
                )

    def _alvos(self, dt):
        """Valores 0..1 de cada ponto de cada linha neste instante."""
        if self.capturador is not None:
            if time.monotonic() - self.capturador.ultimo_bloco > SEM_AUDIO_APOS:
                return [[0.0] * ONDA_N_PONTOS for _ in ONDA_LINHAS]   # silencio
            return self.capturador.analisador.valores
        return self.simulador.atualizar(dt)

    def atualizar(self, dt):
        cx = self.center_x
        cy = self.center_y
        alvos = self._alvos(dt)

        for k, linha in enumerate(self.linhas):
            atual = self.suavizados[k]
            alvo = alvos[k]
            pontos = []
            for i in range(ONDA_N_PONTOS):
                coef = RESPOSTA_ATAQUE if alvo[i] > atual[i] else RESPOSTA_DECAIMENTO
                atual[i] += (alvo[i] - atual[i]) * coef
                t = i / (ONDA_N_PONTOS - 1)
                x = cx + (t - 0.5) * ONDA_LARGURA_AREA
                if ONDA_ESPELHAR:
                    sinal = 1 if (i + k) % 2 == 0 else -1
                else:
                    sinal = 1
                pontos.append(x)
                pontos.append(cy + sinal * atual[i] * ONDA_AMPLITUDE_MAX)
            linha.points = pontos


class AionApp(App):
    def build(self):
        self.title = "Projeto Aura - Aion - Esboco 15"
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
