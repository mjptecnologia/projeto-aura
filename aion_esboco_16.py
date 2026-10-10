"""
Projeto Aura - Aion - Esboco 16
------------------------------------------------------------------------
Sobre a V15 (audio do PC por loopback + espectro real):

  1) MODOS DE LINHA (ONDA_MODO): as tres linhas sobrepostas da V15
     deram confusao visual. Agora e possivel escolher:
        "uma_linha"         -> UMA linha cobrindo todo o espectro
                               (graves a esquerda, agudos a direita).
                               E o padrao: o mais limpo.
        "tres_lado_a_lado"  -> tres linhas, cada uma num terco da
                               largura, formando um espectro continuo
                               com tres cores (sem sobrepor).
        "tres_sobrepostas"  -> como na V15, para comparar.

  2) SIMULACAO DESLIGAVEL (PERMITIR_SIMULACAO = False, o padrao): se o
     audio real nao puder ser aberto, o desenho fica RETO (nada de
     movimento falso) e o console explica o motivo.

  3) FONTE DE AUDIO VISIVEL: o titulo da janela mostra de onde vem o
     audio ("loopback", "microfone", "SIMULACAO" ou "SEM AUDIO"), para
     nao haver duvida sobre o que se esta vendo.

Audio do proprio PC (loopback do Windows), antes do volume do sistema:
    pip install PyAudioWPatch numpy
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
# ======================================================================
try:
    import numpy as np
    import pyaudiowpatch as pyaudio
    AUDIO_LIBS_OK = True
except ImportError:
    AUDIO_LIBS_OK = False

# "loopback" = audio que o PC esta tocando | "microfone" | "simulado"
ORIGEM_AUDIO = "loopback"
# Se o loopback falhar, tenta o microfone antes de desistir?
MICROFONE_COMO_RESERVA = True
# Permite usar a SIMULACAO (movimento falso) quando nao ha audio real,
# ou quando ORIGEM_AUDIO = "simulado". False = nunca simula: sem audio,
# a linha fica reta. (Util no celular/Pydroid: la ponha True.)
PERMITIR_SIMULACAO = False

BLOCKSIZE = 1024        # quadros de audio por bloco (~21 ms a 48 kHz)
TAMANHO_FFT = 4096      # janela da analise (8192 = graves mais detalhados, resposta mais lenta)

# ======================================================================
# Visual
# ======================================================================
COR_FUNDO = (0.0, 0.0, 0.0, 1)

RAIO_NUCLEO = 280
NUCLEO_GRAD_BORDA = (0.25, 0.85, 0.82, 1)
NUCLEO_GRAD_CENTRO = (0.0, 0.0, 0.0, 1)
NUCLEO_GRAD_GAMA = 4.0
TAMANHO_TEXTURA_NUCLEO = 128

# "uma_linha" | "tres_lado_a_lado" | "tres_sobrepostas"
ONDA_MODO = "uma_linha"

COR_BRANCO = (1.0, 1.0, 1.0, 1.0)      # cores SOLIDAS (alpha 1)
COR_CIANO = (0.2, 0.95, 1.0, 1.0)
COR_VERDE_AGUA = (0.45, 1.0, 0.75, 1.0)

ONDA_LARGURA = 2            # espessura da linha
ONDA_LARGURA_AREA = RAIO_NUCLEO * 1.6
ONDA_AMPLITUDE_MAX = RAIO_NUCLEO * 0.35 # (0.55)
# True: pontos alternam acima/abaixo do eixo (forma de onda simetrica).
# False: curva so para cima, estilo grafico de espectro.
ONDA_ESPELHAR = True

# Resposta do desenho (a cada quadro, 60x/seg): mais alto = mais rapido.
# V14: 0.18/0.05 (subida ~200 ms, queda ~750 ms). Aqui: ~70 ms / ~230 ms.
RESPOSTA_ATAQUE = 0.45
RESPOSTA_DECAIMENTO = 0.15

# Controle de ganho / ruido (amplitude relativa ao fundo de escala)
PISO_RUIDO = 0.0005        # abaixo disso vira zero (desenho reto)
PISO_PICO = 0.004          # pico minimo assumido (evita amplificar ruido)
PICO_MEIA_VIDA = 5.0       # segundos para o pico "esquecer" um som alto
CURVA_DINAMICA = 0.6       # <1 realca detalhes fracos (1 = linear)
# Musica tem muito mais energia nos graves que nos agudos; sem
# compensar, so os graves aparecem. Reforca +X dB por oitava acima de
# 200 Hz (e atenua igual abaixo). 0 = desliga a compensacao.
COMPENSACAO_DB_POR_OITAVA = 3.0
COMPENSACAO_FREQ_REF = 200.0

SEM_AUDIO_APOS = 0.25      # s sem blocos de audio => trata como silencio


def montar_linhas(modo):
    """Lista de linhas a desenhar. Cada uma: faixa de frequencia (Hz),
    cor, trecho da largura que ocupa (x0..x1, fracao de 0 a 1) e
    quantidade de pontos."""
    faixas = [(40, 250), (250, 2000), (2000, 8000)]
    cores = [COR_BRANCO, COR_CIANO, COR_VERDE_AGUA]
    if modo == "uma_linha":
        return [{"faixa_hz": (40, 8000), "cor": COR_BRANCO,
                 "x0": 0.0, "x1": 1.0, "n_pontos": 96}]
    if modo == "tres_lado_a_lado":
        return [{"faixa_hz": f, "cor": c, "x0": i / 3, "x1": (i + 1) / 3,
                 "n_pontos": 32} for i, (f, c) in enumerate(zip(faixas, cores))]
    if modo == "tres_sobrepostas":
        return [{"faixa_hz": f, "cor": c, "x0": 0.0, "x1": 1.0,
                 "n_pontos": 64} for f, c in zip(faixas, cores)]
    raise ValueError(f"ONDA_MODO invalido: {modo!r}")


LINHAS = montar_linhas(ONDA_MODO)


# ======================================================================
# Analise de espectro (so numpy - sem Kivy, portanto testavel sozinha)
# ======================================================================
class AnalisadorEspectro:
    """Recebe blocos de audio mono (float -1..1) e produz, para cada
    linha, uma lista de valores 0..1 (energia por faixa de frequencia,
    em escala logaritmica de frequencia)."""

    def __init__(self, samplerate, linhas):
        self.samplerate = samplerate
        self.n = TAMANHO_FFT
        self.buffer = np.zeros(self.n, dtype=np.float32)
        self.janela = np.hanning(self.n).astype(np.float32)
        # amplitude de uma senoide = 2 * |FFT| / soma(janela)
        self.escala = 2.0 / float(self.janela.sum())
        largura_bin = samplerate / self.n
        n_bins = self.n // 2 + 1

        self.faixas = []
        for cfg in linhas:
            f_ini, f_fim = cfg["faixa_hz"]
            bordas = np.geomspace(f_ini, f_fim, cfg["n_pontos"] + 1)
            centros_hz = np.sqrt(bordas[:-1] * bordas[1:])
            # pontos "estreitos" (menos de 2 bins): interpolam entre bins
            # vizinhos, em vez de repetir o mesmo valor em varios pontos
            estreito = (bordas[1:] - bordas[:-1]) / largura_bin < 2.0
            i0 = np.floor(bordas[:-1] / largura_bin).astype(int)
            i1 = np.ceil(bordas[1:] / largura_bin).astype(int)
            i1 = np.maximum(i1, i0 + 2)            # ao menos 2 bins por ponto
            i1 = np.minimum(i1, n_bins)
            i0 = np.minimum(i0, i1 - 1)
            pesos = 10.0 ** (COMPENSACAO_DB_POR_OITAVA
                             * np.log2(centros_hz / COMPENSACAO_FREQ_REF) / 20.0)
            self.faixas.append({
                "i0": i0.tolist(), "i1": i1.tolist(),
                "bins_centro": centros_hz / largura_bin,
                "estreito": estreito, "pesos": pesos,
            })
        self.eixo_bins = np.arange(n_bins, dtype=np.float64)

        self.picos = [PISO_PICO] * len(linhas)
        self.valores = [[0.0] * cfg["n_pontos"] for cfg in linhas]

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
        for k, f in enumerate(self.faixas):
            maximos = np.array([espectro[a:b].max() for a, b in zip(f["i0"], f["i1"])])
            interpolados = np.interp(f["bins_centro"], self.eixo_bins, espectro)
            bruto = np.where(f["estreito"], interpolados, maximos)
            # piso de ruido aplicado ANTES do reforco dos agudos, para o
            # reforco nao transformar ruido de fundo em desenho
            mags = np.maximum(bruto - PISO_RUIDO, 0.0) * f["pesos"]
            self.picos[k] = max(self.picos[k] * decaimento, float(mags.max()), PISO_PICO)
            norm = np.clip(mags / self.picos[k], 0.0, 1.0) ** CURVA_DINAMICA
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
            self.analisador = AnalisadorEspectro(taxa, LINHAS)
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
# Simulacao (so se PERMITIR_SIMULACAO = True; sem numpy)
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
    """Espectro falso, so para ver o visual quando nao ha audio real."""

    def __init__(self, linhas):
        rng = random.Random()
        self.fala = EnvelopeSimulado(rng, 0.25, 0.08, 0.6, 1.8)
        self.pontos = [
            [EnvelopeSimulado(rng, 0.4, 0.15, 0.08, 0.35)
             for _ in range(cfg["n_pontos"])]
            for cfg in linhas
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
        self.status_audio = ""
        self.capturador = self._abrir_audio()
        self.simulador = None
        if self.capturador is None and PERMITIR_SIMULACAO:
            self.simulador = SimuladorEspectro(LINHAS)
            self.status_audio = "SIMULACAO (audio falso)"
        elif self.capturador is None:
            self.status_audio = "SEM AUDIO (veja o console)"
            print("Aion: sem audio real e simulacao desligada "
                  "(PERMITIR_SIMULACAO = False): a linha fica reta.")

        self.suavizados = [[0.0] * cfg["n_pontos"] for cfg in LINHAS]
        self.linhas = []
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
        self.linhas = []
        with self.canvas:
            Color(1, 1, 1, 1)
            Ellipse(
                pos=(cx - RAIO_NUCLEO, cy - RAIO_NUCLEO),
                size=(RAIO_NUCLEO * 2, RAIO_NUCLEO * 2),
                texture=self.textura_nucleo,
            )
            for cfg in LINHAS:
                Color(*cfg["cor"])
                self.linhas.append(
                    Line(points=[0, 0, 0, 0], width=ONDA_LARGURA,
                         cap='round', joint='round')
                )

    def _alvos(self, dt):
        """Valores 0..1 de cada ponto de cada linha neste instante."""
        zeros = [[0.0] * cfg["n_pontos"] for cfg in LINHAS]
        if self.capturador is not None:
            if time.monotonic() - self.capturador.ultimo_bloco > SEM_AUDIO_APOS:
                return zeros                      # silencio: linha reta
            return self.capturador.analisador.valores
        if self.simulador is not None:
            return self.simulador.atualizar(dt)
        return zeros

    def atualizar(self, dt):
        cx = self.center_x
        cy = self.center_y
        alvos = self._alvos(dt)

        for k, (linha, cfg) in enumerate(zip(self.linhas, LINHAS)):
            atual = self.suavizados[k]
            alvo = alvos[k]
            n = cfg["n_pontos"]
            pontos = []
            for i in range(n):
                coef = RESPOSTA_ATAQUE if alvo[i] > atual[i] else RESPOSTA_DECAIMENTO
                atual[i] += (alvo[i] - atual[i]) * coef
                t = i / (n - 1)
                frac_x = cfg["x0"] + t * (cfg["x1"] - cfg["x0"])
                x = cx + (frac_x - 0.5) * ONDA_LARGURA_AREA
                if ONDA_ESPELHAR:
                    sinal = 1 if (i + k) % 2 == 0 else -1
                else:
                    sinal = 1
                pontos.append(x)
                pontos.append(cy + sinal * atual[i] * ONDA_AMPLITUDE_MAX)
            linha.points = pontos


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

        # a fonte do audio aparece no titulo da janela (nao polui o desenho)
        self.title = (f"Aion V16 [{ONDA_MODO}] | {self.nucleo.status_audio}")
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def on_stop(self):
        if self.nucleo.capturador is not None:
            self.nucleo.capturador.parar()


if __name__ == "__main__":
    AionApp().run()
