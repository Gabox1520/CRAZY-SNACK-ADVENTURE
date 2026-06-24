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
ESTADO_OPCIONES  = "opciones"      # Identificador del estado de opciones
ESTADO_FIN_NIVEL = "fin_nivel"     # Identificador del estado de fin de nivel


def main():
    pygame.init()                                                  # Inicializa pygame
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)  # Crea la ventana
    pygame.display.set_caption(TITULO)                              # Título de la ventana
    reloj = pygame.time.Clock()                                     # Reloj para limitar FPS

    # Audio
    audio.inicializar()           # Prepara el sistema de sonido
    audio.reproducir("menu")      # Inicia la música del menú

    # Estado inicial
    estado = ESTADO_MENU          # Comienza en la pantalla de menú

    # Instancias de pantallas persistentes
    pantalla_menu      = PantallaMenu(pantalla)            # Pantalla de menú principal
    pantalla_seleccion = PantallaSeleccion(pantalla)        # Pantalla de selección de escenario
    pantalla_opciones  = PantallaOpciones(pantalla)         # Pantalla de opciones
    pantalla_juego     = None                                # Se crea solo al empezar a jugar
    pantalla_fin       = None                                # Se crea solo al terminar el nivel

    while True:                                              # Bucle principal del juego
        for evento in pygame.event.get():                    # Recorre eventos de la cola
            if evento.type == pygame.QUIT:                    # Si se cierra la ventana
                pygame.quit()                                  # Cierra pygame
                sys.exit()                                      # Termina el programa

            if evento.type == pygame.VIDEORESIZE:               # Si se redimensiona la ventana
                # Mantiene la resolución lógica fija; pygame ya actualiza
                # internamente la superficie de la ventana al redimensionar
                # o maximizar (incluye restaurar desde maximizado).
                pantalla = pygame.display.set_mode(
                    (evento.w, evento.h), pygame.RESIZABLE)      # Ajusta tamaño de ventana
                continue                                          # Pasa al siguiente evento

            nuevo_estado = None                                  # Estado al que se podría cambiar

            if estado == ESTADO_MENU:
                nuevo_estado = pantalla_menu.manejar_evento(evento)        # Procesa evento del menú

            elif estado == ESTADO_SELECCION:
                nuevo_estado = pantalla_seleccion.manejar_evento(evento)   # Procesa evento de selección

            elif estado == ESTADO_OPCIONES:
                nuevo_estado = pantalla_opciones.manejar_evento(evento)    # Procesa evento de opciones

            elif estado == ESTADO_JUEGO and pantalla_juego:
                nuevo_estado = pantalla_juego.manejar_evento(evento)       # Procesa evento del juego

            elif estado == ESTADO_FIN_NIVEL and pantalla_fin:
                nuevo_estado = pantalla_fin.manejar_evento(evento)         # Procesa evento de fin de nivel

            # ── Transiciones de estado ────────────────────────────────────
            if nuevo_estado is not None:                          # Si hubo un cambio solicitado
                if nuevo_estado == ESTADO_SALIR:
                    pygame.quit()                                  # Cierra pygame
                    sys.exit()                                      # Termina el programa

                elif nuevo_estado == ESTADO_JUEGO:
                    idx  = pantalla_seleccion.escenario_elegido     # Escenario elegido por el jugador
                    njug = pantalla_opciones.num_jugadores          # Número de jugadores configurado
                    pantalla_juego = PantallaJuego(pantalla, idx, njug)  # Crea la partida

                elif nuevo_estado == ESTADO_SELECCION:
                    pantalla_seleccion = PantallaSeleccion(pantalla)   # Reinicia pantalla de selección
                    audio.reproducir("seleccion")                       # Cambia música a selección

                elif nuevo_estado == ESTADO_MENU:
                    audio.reproducir("menu")                             # Cambia música al menú

                elif nuevo_estado == ESTADO_OPCIONES:
                    pass   # opciones ya instanciado                     # No requiere acción extra

                elif nuevo_estado == ESTADO_FIN_NIVEL:
                    idx = pantalla_seleccion.escenario_elegido or 0       # Escenario jugado
                    pts = pantalla_juego.puntuacion_final if pantalla_juego else 0  # Puntos obtenidos
                    pantalla_fin = PantallaFinNivel(pantalla, idx, pts)    # Crea pantalla de fin de nivel

                estado = nuevo_estado                                      # Aplica el cambio de estado

        # ── Detectar fin de partida automáticamente ───────────────────────
        if (estado == ESTADO_JUEGO and pantalla_juego                      # Si está jugando
                and pantalla_juego.terminado                                # y la partida ya terminó
                and estado != ESTADO_FIN_NIVEL):                            # y aún no se cambió de estado
            idx = pantalla_seleccion.escenario_elegido or 0                 # Escenario jugado
            pts = pantalla_juego.puntuacion_final                          # Puntuación final
            pantalla_fin = PantallaFinNivel(pantalla, idx, pts)             # Crea pantalla de fin de nivel
            estado = ESTADO_FIN_NIVEL                                       # Cambia al estado de fin de nivel

        # ── Actualizar y dibujar ──────────────────────────────────────────
        if estado == ESTADO_MENU:
            pantalla_menu.actualizar()      # Actualiza animaciones del menú
            pantalla_menu.dibujar()         # Dibuja el menú

        elif estado == ESTADO_SELECCION:
            pantalla_seleccion.actualizar()  # Actualiza animaciones de selección
            pantalla_seleccion.dibujar()     # Dibuja la pantalla de selección

        elif estado == ESTADO_OPCIONES:
            pantalla_opciones.actualizar()   # Actualiza lógica de opciones
            pantalla_opciones.dibujar()      # Dibuja la pantalla de opciones

        elif estado == ESTADO_JUEGO and pantalla_juego:
            pantalla_juego.actualizar()      # Actualiza la lógica de la partida
            pantalla_juego.dibujar()         # Dibuja la partida

        elif estado == ESTADO_FIN_NIVEL and pantalla_fin:
            pantalla_fin.actualizar()        # Actualiza animaciones de fin de nivel
            pantalla_fin.dibujar()           # Dibuja la pantalla de fin de nivel

        pygame.display.flip()    # Actualiza la pantalla visible
        reloj.tick(FPS)           # Limita la velocidad a FPS definidos


if __name__ == "__main__":
    main()    # Punto de entrada del programa
    