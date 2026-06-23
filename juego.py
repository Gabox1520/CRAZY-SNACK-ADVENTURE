# juego.py — Pantalla de juego completa (reemplaza el placeholder)

import pygame
from constantes import *
from cocina import Cocina, DURACION_PARTIDA
from hud import HUD
import audio


class PantallaJuego:
    """
    Orquesta la partida:
    - Instancia Cocina (manager OOP) y HUD
    - Maneja eventos, actualiza y dibuja cada frame
    - Detecta fin de partida y notifica a main
    """

    def __init__(self, pantalla: pygame.Surface,
                 escenario_idx: int = 0,
                 num_jugadores: int = 1):
        self.pantalla       = pantalla
        self.escenario_idx  = escenario_idx if escenario_idx is not None else 0
        self.num_jugadores  = num_jugadores

        # Manager de juego
        self.cocina = Cocina(escenario_idx, num_jugadores)

        # HUD
        self.hud = HUD(escenario_idx)

        # Audio
        audio.reproducir_escenario(escenario_idx)

        # Tiempo total para la barra del HUD
        self._tiempo_total = DURACION_PARTIDA.get(escenario_idx, 120 * 120)

        # Estado interno
        self._pausado = False

    # ── Eventos ──────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                audio.detener()
                return ESTADO_SELECCION
            if evento.key == pygame.K_p:
                self._pausado = not self._pausado
                if self._pausado:
                    audio.pausar()
                else:
                    audio.reanudar()

        if not self._pausado:
            self.cocina.manejar_evento(evento)

        return None

    # ── Actualizar ───────────────────────────────────────────────────────────
    def actualizar(self):
        if self._pausado:
            return

        self.cocina.actualizar()

        # Cuando termina el tiempo, detener música
        if self.cocina.terminado:
            audio.detener()

    # ── Dibujar ──────────────────────────────────────────────────────────────
    def dibujar(self):
        # El mapa y los chefs
        self.cocina.dibujar(self.pantalla)

        # HUD encima
        self.hud.dibujar(
            self.pantalla,
            self.cocina.tiempo_restante,
            self._tiempo_total,
            self.cocina.puntuacion,
            self.cocina.recetas_activas,
            self.cocina.chefs,
        )

        # Pausa overlay
        if self._pausado:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.pantalla.blit(overlay, (0, 0))
            f = pygame.font.SysFont("impact", 64)
            txt = f.render("PAUSA", True, AMARILLO)
            self.pantalla.blit(txt, (ANCHO // 2 - txt.get_width() // 2,
                                      ALTO // 2 - txt.get_height() // 2))
            f2 = pygame.font.SysFont("impact", 22)
            sub = f2.render("P = reanudar  |  ESC = volver al menú",
                            True, CREMA)
            self.pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2,
                                      ALTO // 2 + 50))

    # ── Propiedad para que main sepa si terminó ───────────────────────────────
    @property
    def terminado(self) -> bool:
        return self.cocina.terminado

    @property
    def puntuacion_final(self) -> int:
        return self.cocina.puntuacion
