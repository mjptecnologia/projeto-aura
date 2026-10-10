"""
Projeto Aura - Aion (versao de IMPLANTACAO, baseada na V16 ajustada)
------------------------------------------------------------------------
O VISUAL e o da V16 que Marlon aprovou e ajustou (linha fina, amplitude
reduzida). Sobre ela, esta versao acrescenta o que e preciso para rodar
no PC Aura (Debian) sem mexer no desenho:

  - ESCALA: o desenho acompanha o tamanho da janela/tela (referencia:
    janela de 700x700 = identico a V16). Em retrato 900x1440 ele cresce
    proporcionalmente.
  - TELA CHEIA / QUIOSQUE: --tela-cheia (esconde o cursor).
  - AUDIO MULTIPLATAFORMA: Windows = PyAudioWPatch (loopback do PC e
    microfone); Linux = sounddevice (microfone). Sem biblioteca ou sem
    dispositivo, a linha fica reta (nunca inventa movimento).
  - OPCOES DE LINHA DE COMANDO (para testar sem editar o codigo):
        --simular            forca a simulacao (movimento falso)
        --audio X            loopback | microfone | nenhum
        --tela-cheia         tela cheia, sem cursor
        --tamanho LxA        janela sem borda de LARGURAxALTURA (ex.: 900x1440)
        --fps                mostra os quadros por segundo a cada 5 s
        --sair-em SEG        fecha sozinho depois de SEG segundos (seguranca)

Sem nenhuma opcao, o comportamento e o da V16 (janela 700x700).
"""

import argparse
import os

# o Kivy nao deve tentar interpretar as nossas opcoes de linha de comando
os.environ.setdefault("KIVY_NO_ARGS", "1")


def _tamanho(texto):
    try:
        larg, alt = texto.lower().split("x")
        larg, alt = int(larg), int(alt)
        if larg < 100 or alt < 100:
            raise ValueError
        return larg, alt
    except ValueError:
        raise argparse.ArgumentTypeError("use LARGURAxALTURA, ex.: 900x1440")


def _ler_argumentos():
    p = argparse.ArgumentParser(description="Projeto Aura - Aion")
    p.add_argument("--simular", action="store_true",
                   help="forca a simulacao (movimento falso, sem audio)")
    p.add_argument("--audio", choices=("loopback", "microfone", "nenhum"),
                   help="fonte do audio")
    p.add_argument("--tela-cheia", action="store_true",
                   help="tela cheia, sem cursor")
    p.add_argument("--tamanho", type=_tamanho, metavar="LxA",
                   help="janela sem borda com este tamanho, ex.: 900x1440")
    p.add_argument("--fps", action="store_true",
                   help="mostra os quadros por segundo a cada 5 s")
    p.add_argument("--sair-em", type=float, metavar="SEG",
                   help="fecha sozinho depois de SEG segundos")
    args, _ = p.parse_known_args()
    return args


ARGS = _ler_argumentos()

from kivy.config import Config
if ARGS.tamanho:
    Config.set('graphics', 'width', str(ARGS.tamanho[0]))
    Config.set('graphics', 'height', str(ARGS.tamanho[1]))
    Config.set('graphics', 'borderless', '1')
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'left', '0')
    Config.set('graphics', 'top', '0')
    Config.set('graphics', 'resizable', '0')
else:
    Config.set('graphics', 'width', '700')
    Config.set('graphics', 'height', '700')
    Config.set('graphics', 'resizable', True)
if ARGS.tela_cheia:
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'show_cursor', '0')

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
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False
try:
    import pyaudiowpatch as pyaudio      # Windows: loopback do PC e microfone
    PYAUDIOWPATCH_OK = True
except ImportError:
    PYAUDIOWPATCH_OK = False
try:
    import sounddevice as sd             # Linux: microfone
    SOUNDDEVICE_OK = True
except (ImportError, OSError):           # OSError = falta a libportaudio2
    SOUNDDEVICE_OK = False

# "loopback" = audio que o PC esta tocando | "microfone" | "simulado"
ORIGEM_AUDIO = "loopback"
# Se o loopback falhar, tenta o microfone antes de desistir?
MICROFONE_COMO_RESERVA = True
# Permite usar a SIMULACAO (movimento falso) quando nao ha audio real,
# ou quando ORIGEM_AUDIO = "simulado". False = nunca simula: sem audio,
# a linha fica reta. (Util no celular/Pydroid: la ponha True.)
PERMITIR_SIMULACAO = False

# opcoes de linha de comando sobrepoem as constantes acima
if ARGS.simular:
    PERMITIR_SIMULACAO = True
    ORIGEM_AUDIO = "simulado"
elif ARGS.audio == "nenhum":
    ORIGEM_AUDIO = "simulado"      # "sem audio": nao abre nada
elif ARGS.audio:
    ORIGEM_AUDIO = ARGS.audio

BLOCKSIZE = 1024        # quadros de audio por bloco (~21 ms a 48 kHz)
TAMANHO_FFT = 4096      # janela da analise (8192 = graves mais detalhados, resposta mais lenta)

# ======================================================================
# Visual
# ======================================================================
COR_FUNDO = (0.0, 0.0, 0.0, 1)

REF_TAMANHO = 700          # janela de referencia (700x700 = visual identico a V16)
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


class CapturadorSounddevice:
    """Captura o MICROFONE via sounddevice (Linux). Nao faz loopback:
    isso so existe no Windows (PyAudioWPatch)."""

    def __init__(self, origem):
        if origem != "microfone":
            raise RuntimeError("loopback so existe no Windows (PyAudioWPatch); "
                               "use --audio microfone")
        self.stream = None
        self.analisador = None
        self.ultimo_bloco = 0.0
        self.origem = origem
        self.nome = ""
        try:
            info = sd.query_devices(kind="input")
            taxa = int(info["default_samplerate"])
            self.nome = info["name"]
            self.analisador = AnalisadorEspectro(taxa, LINHAS)
            self.stream = sd.InputStream(
                samplerate=taxa, channels=1, blocksize=BLOCKSIZE,
                dtype="float32", callback=self._callback,
            )
            self.stream.start()
        except Exception:
            self.parar()
            raise

    def _callback(self, indata, frames, time_info, status):
        try:
            self.analisador.processar(indata[:, 0].copy())
            self.ultimo_bloco = time.monotonic()
        except Exception:
            pass

    def parar(self):
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
        except Exception:
            pass


def criar_capturador(origem):
    """Windows (PyAudioWPatch) tem prioridade; senao, sounddevice."""
    if PYAUDIOWPATCH_OK:
        return CapturadorAudio(origem)
    if SOUNDDEVICE_OK:
        return CapturadorSounddevice(origem)
    raise RuntimeError("nenhuma biblioteca de audio instalada")


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
        self.escala = 1.0
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
            print("Aion: sem captura de audio (modo simulado / --audio nenhum).")
            return None
        if not NUMPY_OK:
            print("Aion: falta o numpy -> pip install numpy")
            return None
        if not (PYAUDIOWPATCH_OK or SOUNDDEVICE_OK):
            print("Aion: nenhuma biblioteca de audio instalada. "
                  "Windows: pip install PyAudioWPatch numpy | "
                  "Linux: apt install libportaudio2 e pip install sounddevice numpy")
            return None
        tentativas = [ORIGEM_AUDIO]
        if ORIGEM_AUDIO == "loopback" and MICROFONE_COMO_RESERVA:
            tentativas.append("microfone")
        for origem in tentativas:
            try:
                cap = criar_capturador(origem)
                self.status_audio = f"audio real: {origem} - {cap.nome}"
                print(f"Aion: {self.status_audio}")
                return cap
            except Exception as erro:
                print(f"Aion: nao consegui abrir '{origem}' ({erro}).")
        return None

    def montar(self, *args):
        self.canvas.clear()
        # escala: o desenho acompanha o tamanho da janela/tela
        self.escala = max(0.1, min(self.width, self.height) / REF_TAMANHO)
        cx = self.center_x
        cy = self.center_y
        raio = RAIO_NUCLEO * self.escala
        self.linhas = []
        with self.canvas:
            Color(1, 1, 1, 1)
            Ellipse(
                pos=(cx - raio, cy - raio),
                size=(raio * 2, raio * 2),
                texture=self.textura_nucleo,
            )
            for cfg in LINHAS:
                Color(*cfg["cor"])
                self.linhas.append(
                    Line(points=[0, 0, 0, 0],
                         width=max(1.0, ONDA_LARGURA * self.escala),
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
        area = ONDA_LARGURA_AREA * self.escala
        amplitude = ONDA_AMPLITUDE_MAX * self.escala
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
                x = cx + (frac_x - 0.5) * area
                if ONDA_ESPELHAR:
                    sinal = 1 if (i + k) % 2 == 0 else -1
                else:
                    sinal = 1
                pontos.append(x)
                pontos.append(cy + sinal * atual[i] * amplitude)
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
        self.title = f"Aion [{ONDA_MODO}] | {self.nucleo.status_audio}"

        if ARGS.fps:
            Clock.schedule_interval(
                lambda dt: print(f"Aion: {Clock.get_fps():.1f} FPS"), 5)
        if ARGS.sair_em:
            Clock.schedule_once(lambda dt: self.stop(), ARGS.sair_em)
        return root

    def _atualizar_fundo(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def on_stop(self):
        if self.nucleo.capturador is not None:
            self.nucleo.capturador.parar()


if __name__ == "__main__":
    AionApp().run()
