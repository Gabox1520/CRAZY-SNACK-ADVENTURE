# audio.py — Sistema de audio: música por pantalla y control de volumen

import pygame
import os

# Nombres de archivos de audio (colócalos en la carpeta assets/audio/)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")   # Ruta base de los audios

MUSICAS = {
    "menu":         "menu_music.mp3",     # Música del menú principal
    "seleccion":    "menu_music.mp3",     # Música de la pantalla de selección
    "soda_tica":    "soda_tica.mp3",      # Música del escenario Soda Tica
    "pizzeria":     "pizzeria.mp3",       # Música del escenario Pizzería
    "sushi":        "sushi.mp3",          # Música del escenario Sushi
    "game_over":    "menu_music.mp3",     # Música al terminar la partida
}

MUSICA_POR_ESCENARIO = {
    0: "soda_tica",    # Escenario 0 usa la pista de Soda Tica
    1: "pizzeria",      # Escenario 1 usa la pista de Pizzería
    2: "sushi",          # Escenario 2 usa la pista de Sushi
}

_musica_actual: str | None = None    # Clave de la música que está sonando
_volumen: float = 0.7                 # 0.0 – 1.0    # Volumen actual del sistema


def inicializar():
    """Llama una sola vez al inicio (pygame.mixer ya debe estar inicializado)."""
    if not pygame.mixer.get_init():                                       # Si el mixer no está iniciado
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Lo inicializa
    pygame.mixer.music.set_volume(_volumen)    # Aplica el volumen configurado


def reproducir(clave: str, loop: bool = True):
    """
    Reproduce la música indicada por clave (ej. 'menu', 'soda_tica').
    Si ya está sonando la misma, no hace nada.
    """
    global _musica_actual
    if clave == _musica_actual:    # Si ya está sonando esa misma pista
        return
    ruta = os.path.join(AUDIO_DIR, MUSICAS.get(clave, ""))   # Construye la ruta del archivo
    if not os.path.isfile(ruta):                              # Si el archivo no existe
        # Sin archivo: continúa en silencio sin lanzar error
        _musica_actual = clave                                  # Igual marca la clave como actual
        return
    pygame.mixer.music.stop()                  # Detiene la música anterior
    pygame.mixer.music.load(ruta)               # Carga el nuevo archivo
    pygame.mixer.music.play(-1 if loop else 0)  # Reproduce en bucle o una vez
    pygame.mixer.music.set_volume(_volumen)     # Aplica el volumen actual
    _musica_actual = clave                       # Actualiza la pista activa


def reproducir_escenario(escenario_idx: int):
    clave = MUSICA_POR_ESCENARIO.get(escenario_idx, "menu")   # Obtiene la clave de música del escenario
    reproducir(clave)                                           # Reproduce esa música


def detener():
    pygame.mixer.music.stop()    # Detiene la música actual
    global _musica_actual
    _musica_actual = None         # Limpia la referencia de pista activa


def pausar():
    pygame.mixer.music.pause()    # Pausa la música sin detenerla


def reanudar():
    pygame.mixer.music.unpause()   # Reanuda la música pausada


def set_volumen(v: float):
    """Establece el volumen (0.0 – 1.0)."""
    global _volumen
    _volumen = max(0.0, min(1.0, v))           # Limita el valor entre 0 y 1
    pygame.mixer.music.set_volume(_volumen)    # Aplica el nuevo volumen


def get_volumen() -> float:
    return _volumen    # Retorna el volumen actual
