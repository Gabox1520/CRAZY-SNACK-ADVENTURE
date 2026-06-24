# juego.py — Pantalla de juego completa (reemplaza el placeholder)

import pygame                                  # Librería del motor del juego
from constantes import *                       # Colores, tamaños y estados globales
from cocina import Cocina, DURACION_PARTIDA    # Manager de la partida y duración por escenario
from hud import HUD                            # Interfaz de pedidos, tiempo y puntuación
import audio                                   # Control de música y sonido


class PantallaJuego:

    def __init__(self, pantalla: pygame.Surface,
                 escenario_idx: int = 0,
                 num_jugadores: int = 1):
        self.pantalla       = pantalla                                       # Superficie donde se dibuja
        self.escenario_idx  = escenario_idx if escenario_idx is not None else 0  # Índice del restaurante elegido
        self.num_jugadores  = num_jugadores                                  # 1 o 2 jugadores

        # Manejo del juego
        self.cocina = Cocina(escenario_idx, num_jugadores)  # Crea mapa, chefs y recetas

        # HUD
        self.hud = HUD(escenario_idx)  # Crea la interfaz visual del escenario

        # Audio
        audio.reproducir_escenario(escenario_idx)  # Inicia la música del escenario

        # Tiempo total para la barra del HUD
        self._tiempo_total = DURACION_PARTIDA.get(escenario_idx, 120 * 120)  # Duración total en frames

        # Estado interno
        self._pausado = False  # Bandera de pausa

    # ── Eventos ──────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.KEYDOWN:               # Si se presionó una tecla
            if evento.key == pygame.K_ESCAPE:            # ESC vuelve al menú de selección
                audio.detener()                          # Detiene la música
                return ESTADO_SELECCION                  # Cambia de pantalla
            if evento.key == pygame.K_p:                 # P alterna pausa
                self._pausado = not self._pausado         # Invierte el estado de pausa
                if self._pausado:
                    audio.pausar()                       # Pausa la música
                else:
                    audio.reanudar()                     # Reanuda la música

        if not self._pausado:                            # Solo procesa juego si no está en pausa
            self.cocina.manejar_evento(evento)           # Delega el evento a la cocina

        return None                                      # Sin cambio de pantalla

    # ── Actualizar ───────────────────────────────────────────────────────────
    def actualizar(self):
        if self._pausado:                                # Si está pausado, no actualiza nada
            return

        self.cocina.actualizar()                         # Avanza lógica de la partida un frame

        # Cuando termina el tiempo, detener música
        if self.cocina.terminado:                        # Si la partida ya terminó
            audio.detener()                              # Corta la música

    # ── Dibujar ──────────────────────────────────────────────────────────────
    def dibujar(self):
        # El mapa y los chefs
        self.cocina.dibujar(self.pantalla)               # Dibuja mapa, estaciones y chefs

        # HUD encima
        self.hud.dibujar(
            self.pantalla,                               # Superficie destino
            self.cocina.tiempo_restante,                 # Tiempo restante actual
            self._tiempo_total,                          # Tiempo total (para la barra)
            self.cocina.puntuacion,                      # Puntuación actual
            self.cocina.recetas_activas,                 # Lista de pedidos activos
            self.cocina.chefs,                           # Lista de chefs en juego
        )

        # Pausa overlay
        if self._pausado:                                                  # Solo si está en pausa
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)        # Capa semitransparente
            overlay.fill((0, 0, 0, 140))                                   # Negro translúcido
            self.pantalla.blit(overlay, (0, 0))                           # Cubre toda la pantalla
            f = pygame.font.SysFont("impact", 64)                         # Fuente grande para "PAUSA"
            txt = f.render("PAUSA", True, AMARILLO)                       # Renderiza el texto
            self.pantalla.blit(txt, (ANCHO // 2 - txt.get_width() // 2,   # Centra horizontalmente
                                      ALTO // 2 - txt.get_height() // 2)) # Centra verticalmente
            f2 = pygame.font.SysFont("impact", 22)                        # Fuente pequeña para subtítulo
            sub = f2.render("P = reanudar  |  ESC = volver al menú",      # Texto de ayuda
                            True, CREMA)
            self.pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2,   # Centra horizontalmente
                                      ALTO // 2 + 50))                    # Debajo del texto "PAUSA"

    # ── Propiedad para que main sepa si terminó ───────────────────────────────
    @property
    def terminado(self) -> bool:
        return self.cocina.terminado                     # Expone si la partida acabó

    @property
    def puntuacion_final(self) -> int:
        return self.cocina.puntuacion                     # Expone la puntuación final
    