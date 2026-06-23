# main.py — Entry point de Crazy Snack Rush TEC

import pygame
import sys

from constantes import *
from menu import PantallaMenu
from seleccion_escenario import PantallaSeleccion
from juego import PantallaJuego
from opciones import PantallaOpciones
from fin_nivel import PantallaFinNivel
import audio

# Estado extra para opciones y fin de nivel
ESTADO_OPCIONES  = "opciones"
ESTADO_FIN_NIVEL = "fin_nivel"


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption(TITULO)
    reloj = pygame.time.Clock()

    # Audio
    audio.inicializar()
    audio.reproducir("menu")

    # Estado inicial
    estado = ESTADO_MENU

    # Instancias de pantallas persistentes
    pantalla_menu      = PantallaMenu(pantalla)
    pantalla_seleccion = PantallaSeleccion(pantalla)
    pantalla_opciones  = PantallaOpciones(pantalla)
    pantalla_juego     = None
    pantalla_fin       = None

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.VIDEORESIZE:
                # Mantiene la resolución lógica fija; pygame ya actualiza
                # internamente la superficie de la ventana al redimensionar
                # o maximizar (incluye restaurar desde maximizado).
                pantalla = pygame.display.set_mode(
                    (evento.w, evento.h), pygame.RESIZABLE)
                continue

            nuevo_estado = None

            if estado == ESTADO_MENU:
                nuevo_estado = pantalla_menu.manejar_evento(evento)

            elif estado == ESTADO_SELECCION:
                nuevo_estado = pantalla_seleccion.manejar_evento(evento)

            elif estado == ESTADO_OPCIONES:
                nuevo_estado = pantalla_opciones.manejar_evento(evento)

            elif estado == ESTADO_JUEGO and pantalla_juego:
                nuevo_estado = pantalla_juego.manejar_evento(evento)

            elif estado == ESTADO_FIN_NIVEL and pantalla_fin:
                nuevo_estado = pantalla_fin.manejar_evento(evento)

            # ── Transiciones de estado ────────────────────────────────────
            if nuevo_estado is not None:
                if nuevo_estado == ESTADO_SALIR:
                    pygame.quit()
                    sys.exit()

                elif nuevo_estado == ESTADO_JUEGO:
                    idx  = pantalla_seleccion.escenario_elegido
                    njug = pantalla_opciones.num_jugadores
                    pantalla_juego = PantallaJuego(pantalla, idx, njug)

                elif nuevo_estado == ESTADO_SELECCION:
                    pantalla_seleccion = PantallaSeleccion(pantalla)
                    audio.reproducir("seleccion")

                elif nuevo_estado == ESTADO_MENU:
                    audio.reproducir("menu")

                elif nuevo_estado == ESTADO_OPCIONES:
                    pass   # opciones ya instanciado

                elif nuevo_estado == ESTADO_FIN_NIVEL:
                    idx = pantalla_seleccion.escenario_elegido or 0
                    pts = pantalla_juego.puntuacion_final if pantalla_juego else 0
                    pantalla_fin = PantallaFinNivel(pantalla, idx, pts)

                estado = nuevo_estado

        # ── Detectar fin de partida automáticamente ───────────────────────
        if (estado == ESTADO_JUEGO and pantalla_juego
                and pantalla_juego.terminado
                and estado != ESTADO_FIN_NIVEL):
            idx = pantalla_seleccion.escenario_elegido or 0
            pts = pantalla_juego.puntuacion_final
            pantalla_fin = PantallaFinNivel(pantalla, idx, pts)
            estado = ESTADO_FIN_NIVEL

        # ── Actualizar y dibujar ──────────────────────────────────────────
        if estado == ESTADO_MENU:
            pantalla_menu.actualizar()
            pantalla_menu.dibujar()

        elif estado == ESTADO_SELECCION:
            pantalla_seleccion.actualizar()
            pantalla_seleccion.dibujar()

        elif estado == ESTADO_OPCIONES:
            pantalla_opciones.actualizar()
            pantalla_opciones.dibujar()

        elif estado == ESTADO_JUEGO and pantalla_juego:
            pantalla_juego.actualizar()
            pantalla_juego.dibujar()

        elif estado == ESTADO_FIN_NIVEL and pantalla_fin:
            pantalla_fin.actualizar()
            pantalla_fin.dibujar()

        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    main()