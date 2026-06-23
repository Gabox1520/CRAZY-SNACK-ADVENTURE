# audio.py — Sistema de audio: música por pantalla y control de volumen

import pygame
import os

# Nombres de archivos de audio (colócalos en la carpeta assets/audio/)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

MUSICAS = {
    "menu":         "menu_music.mp3",
    "seleccion":    "menu_music.mp3",
    "soda_tica":    "soda_tica.mp3",
    "pizzeria":     "pizzeria.mp3",
    "sushi":        "sushi.mp3",
    "game_over":    "menu_music.mp3",
}

MUSICA_POR_ESCENARIO = {
    0: "soda_tica",
    1: "pizzeria",
    2: "sushi",
}

_musica_actual: str | None = None
_volumen: float = 0.7   # 0.0 – 1.0


def inicializar():
    """Llama una sola vez al inicio (pygame.mixer ya debe estar inicializado)."""
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.music.set_volume(_volumen)


def reproducir(clave: str, loop: bool = True):
    """
    Reproduce la música indicada por clave (ej. 'menu', 'soda_tica').
    Si ya está sonando la misma, no hace nada.
    """
    global _musica_actual
    if clave == _musica_actual:
        return
    ruta = os.path.join(AUDIO_DIR, MUSICAS.get(clave, ""))
    if not os.path.isfile(ruta):
        # Sin archivo: continúa en silencio sin lanzar error
        _musica_actual = clave
        return
    pygame.mixer.music.stop()
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play(-1 if loop else 0)
    pygame.mixer.music.set_volume(_volumen)
    _musica_actual = clave


def reproducir_escenario(escenario_idx: int):
    clave = MUSICA_POR_ESCENARIO.get(escenario_idx, "menu")
    reproducir(clave)


def detener():
    pygame.mixer.music.stop()
    global _musica_actual
    _musica_actual = None


def pausar():
    pygame.mixer.music.pause()


def reanudar():
    pygame.mixer.music.unpause()


def set_volumen(v: float):
    """Establece el volumen (0.0 – 1.0)."""
    global _volumen
    _volumen = max(0.0, min(1.0, v))
    pygame.mixer.music.set_volume(_volumen)


def get_volumen() -> float:
    return _volumen
