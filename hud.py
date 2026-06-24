# hud.py — HUD: cola de pedidos, temporizador, puntuación, controles

import pygame
import math
from constantes import *
from recetas import Receta

HUD_ALTO_SUP = 80   # altura de la banda superior      # Alto en píxeles de la banda de arriba
HUD_ALTO_INF = 90   # altura de la banda inferior       # Alto en píxeles de la banda de abajo


class HUD:
    """
    Dibuja toda la interfaz superpuesta al mapa:
    - Banda superior: timer, puntuación, nombre del escenario
    - Banda inferior: cola de recetas activas con countdown visual
    - Indicadores de chefs activos
    """

    NOMBRES_ESC = ["Soda Tica", "Pizzería Roma", "Sushi Bar Kyoto"]    # Nombres de escenarios

    def __init__(self, escenario_idx: int):
        self.escenario_idx = escenario_idx                            # Índice del escenario
        self.nombre_esc    = self.NOMBRES_ESC[escenario_idx]          # Nombre del escenario actual

        self.f_grande = pygame.font.SysFont("impact", 32)    # Fuente grande (título/timer)
        self.f_media  = pygame.font.SysFont("impact", 20)    # Fuente media (etiquetas)
        self.f_small  = pygame.font.SysFont("arial",  14)    # Fuente pequeña (nombres receta)
        self.f_tiny   = pygame.font.SysFont("arial",  12)    # Fuente diminuta (detalles)

    def dibujar(self, surface: pygame.Surface,
                tiempo_restante: int,
                tiempo_total: int,
                puntuacion: int,
                recetas: list[Receta],
                chefs: list):

        self._dibujar_banda_superior(surface, tiempo_restante,
                                     tiempo_total, puntuacion)     # Dibuja timer y puntuación
        self._dibujar_banda_inferior(surface, recetas)            # Dibuja cola de pedidos
        self._dibujar_indicadores_chef(surface, chefs)            # Dibuja info de cada chef

    # ── Banda superior ───────────────────────────────────────────────────────
    def _dibujar_banda_superior(self, surface, tiempo_restante,
                                 tiempo_total, puntuacion):
        pygame.draw.rect(surface, NEGRO, (0, 0, ANCHO, HUD_ALTO_SUP))      # Fondo negro de la banda
        pygame.draw.line(surface, NARANJA, (0, HUD_ALTO_SUP),
                         (ANCHO, HUD_ALTO_SUP), 3)                          # Línea inferior de la banda

        # Nombre del restaurante
        nom = self.f_grande.render(self.nombre_esc, True, NARANJA_VIV)     # Texto del nombre
        surface.blit(nom, (ANCHO // 2 - nom.get_width() // 2, 8))         # Centrado horizontal

        # Puntuación
        pts_txt = self.f_media.render(f"⭐ {puntuacion}", True, AMARILLO) # Texto de puntuación
        surface.blit(pts_txt, (20, 30))                                    # Esquina superior izquierda

        # Temporizador
        segundos = tiempo_restante // 120                                  # Convierte frames a segundos
        mins     = segundos // 60                                          # Minutos restantes
        segs     = segundos % 60                                           # Segundos restantes
        color_t  = ROJO if segundos < 30 else CREMA                        # Rojo si queda poco tiempo
        # Parpadeo en los últimos 10 s
        if segundos < 10 and (tiempo_restante // 30) % 2 == 0:
            color_t = NEGRO                                                # Hace parpadear el texto
        timer_txt = self.f_grande.render(f"⏱ {mins:01d}:{segs:02d}", True, color_t)  # Texto del timer
        surface.blit(timer_txt, (ANCHO - timer_txt.get_width() - 20, 8))   # Esquina superior derecha

        # Barra de tiempo
        barra_w = 200                                                       # Ancho de la barra
        barra_x = ANCHO - barra_w - 20                                      # Posición x de la barra
        barra_y = 52                                                        # Posición y de la barra
        frac    = tiempo_restante / max(tiempo_total, 1)                   # Fracción de tiempo restante
        col_b   = VERDE if frac > 0.5 else (AMARILLO if frac > 0.25 else ROJO)  # Color según fracción
        pygame.draw.rect(surface, GRIS_OSC, (barra_x, barra_y, barra_w, 12),
                         border_radius=6)                                   # Fondo de la barra
        pygame.draw.rect(surface, col_b,
                         (barra_x, barra_y, int(barra_w * frac), 12),
                         border_radius=6)                                   # Relleno según tiempo

    # ── Banda inferior — cola de recetas ─────────────────────────────────────
    def _dibujar_banda_inferior(self, surface, recetas: list[Receta]):
        y0 = ALTO - HUD_ALTO_INF                                            # Posición y de la banda
        pygame.draw.rect(surface, NEGRO, (0, y0, ANCHO, HUD_ALTO_INF))      # Fondo negro
        pygame.draw.line(surface, NARANJA, (0, y0), (ANCHO, y0), 3)         # Línea superior de la banda

        label = self.f_media.render("PEDIDOS:", True, CREMA)                # Etiqueta "PEDIDOS:"
        surface.blit(label, (10, y0 + 8))                                   # Dibuja la etiqueta

        tarj_w = 160        # Ancho de cada tarjeta de receta
        tarj_h = 70         # Alto de cada tarjeta de receta
        margen  = 8         # Espacio entre tarjetas
        x       = 110       # Posición x inicial de la primera tarjeta

        for rec in recetas[:5]:   # máximo 5 en pantalla
            rect = pygame.Rect(x, y0 + 8, tarj_w, tarj_h)                   # Rectángulo de la tarjeta

            # Fondo tarjeta
            frac = rec.progreso_tiempo()                                    # Fracción de tiempo restante
            col_borde = (VERDE if frac > 0.5 else
                         AMARILLO if frac > 0.25 else ROJO)                 # Color según urgencia
            pygame.draw.rect(surface, GRIS_OSC, rect, border_radius=6)      # Fondo de la tarjeta
            pygame.draw.rect(surface, col_borde, rect, width=2, border_radius=6)  # Borde de la tarjeta

            # Nombre receta
            nom = self.f_small.render(rec.nombre, True, CREMA)              # Nombre del platillo
            surface.blit(nom, (rect.x + 4, rect.y + 4))                    # Dibuja el nombre

            # Puntos actuales
            pts = self.f_tiny.render(f"★ {rec.puntos_receta}", True, AMARILLO)  # Puntos actuales
            surface.blit(pts, (rect.x + 4, rect.y + 20))                   # Dibuja los puntos

            # Ingredientes requeridos
            ings_txt = ", ".join(rec.nombres_requeridos)                    # Lista de ingredientes
            if len(ings_txt) > 22:
                ings_txt = ings_txt[:21] + "…"                              # Trunca si es muy largo
            ing_surf = self.f_tiny.render(ings_txt, True, GRIS_MED)         # Renderiza ingredientes
            surface.blit(ing_surf, (rect.x + 4, rect.y + 34))              # Dibuja la lista

            # Barra de tiempo de la receta
            bw = tarj_w - 8                                                  # Ancho de la barra interna
            pygame.draw.rect(surface, NEGRO,
                             (rect.x + 4, rect.bottom - 14, bw, 8),
                             border_radius=4)                                # Fondo de la barra
            pygame.draw.rect(surface, col_borde,
                             (rect.x + 4, rect.bottom - 14,
                              int(bw * frac), 8),
                             border_radius=4)                                # Relleno según tiempo

            x += tarj_w + margen                                             # Avanza posición para la siguiente

    # ── Indicadores de chef ───────────────────────────────────────────────────
    def _dibujar_indicadores_chef(self, surface, chefs):
        colores = [(220, 80, 40), (40, 120, 220)]          # Colores por jugador
        nombres = ["J1: WASD / Q", "J2: IJKL / U"]          # Etiquetas de controles
        for i, chef in enumerate(chefs):                    # Por cada chef en juego
            x = 20 + i * 200                                 # Posición x según índice
            y = HUD_ALTO_SUP + 8                              # Posición y debajo de la banda superior
            pygame.draw.circle(surface, colores[i], (x + 10, y + 10), 10)        # Círculo de color
            pygame.draw.circle(surface, BLANCO, (x + 10, y + 10), 10, 2)         # Borde blanco
            txt = self.f_tiny.render(nombres[i], True, colores[i])               # Texto de controles
            surface.blit(txt, (x + 24, y + 3))                                  # Dibuja el texto
            # Ingrediente en mano
            if chef.ingrediente_en_mano:                                         # Si el chef trae algo
                ing = chef.ingrediente_en_mano                                   # Ingrediente actual
                col = VERDE if ing.esta_listo else (ROJO if ing.esta_quemado else CREMA)  # Color según estado
                ing_txt = self.f_tiny.render(
                    f"→ {ing.nombre} [{ing.estado}]", True, col)                 # Texto del ingrediente
                surface.blit(ing_txt, (x + 24, y + 18))                          # Dibuja debajo del nombre
                