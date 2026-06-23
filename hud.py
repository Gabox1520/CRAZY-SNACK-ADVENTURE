# hud.py — HUD: cola de pedidos, temporizador, puntuación, controles

import pygame
import math
from constantes import *
from recetas import Receta

HUD_ALTO_SUP = 80   # altura de la banda superior
HUD_ALTO_INF = 90   # altura de la banda inferior


class HUD:
    """
    Dibuja toda la interfaz superpuesta al mapa:
    - Banda superior: timer, puntuación, nombre del escenario
    - Banda inferior: cola de recetas activas con countdown visual
    - Indicadores de chefs activos
    """

    NOMBRES_ESC = ["Soda Tica", "Pizzería Roma", "Sushi Bar Kyoto"]

    def __init__(self, escenario_idx: int):
        self.escenario_idx = escenario_idx
        self.nombre_esc    = self.NOMBRES_ESC[escenario_idx]

        self.f_grande = pygame.font.SysFont("impact", 32)
        self.f_media  = pygame.font.SysFont("impact", 20)
        self.f_small  = pygame.font.SysFont("arial",  14)
        self.f_tiny   = pygame.font.SysFont("arial",  12)

    def dibujar(self, surface: pygame.Surface,
                tiempo_restante: int,
                tiempo_total: int,
                puntuacion: int,
                recetas: list[Receta],
                chefs: list):

        self._dibujar_banda_superior(surface, tiempo_restante,
                                     tiempo_total, puntuacion)
        self._dibujar_banda_inferior(surface, recetas)
        self._dibujar_indicadores_chef(surface, chefs)

    # ── Banda superior ───────────────────────────────────────────────────────
    def _dibujar_banda_superior(self, surface, tiempo_restante,
                                 tiempo_total, puntuacion):
        pygame.draw.rect(surface, NEGRO, (0, 0, ANCHO, HUD_ALTO_SUP))
        pygame.draw.line(surface, NARANJA, (0, HUD_ALTO_SUP),
                         (ANCHO, HUD_ALTO_SUP), 3)

        # Nombre del restaurante
        nom = self.f_grande.render(self.nombre_esc, True, NARANJA_VIV)
        surface.blit(nom, (ANCHO // 2 - nom.get_width() // 2, 8))

        # Puntuación
        pts_txt = self.f_media.render(f"⭐ {puntuacion}", True, AMARILLO)
        surface.blit(pts_txt, (20, 30))

        # Temporizador
        segundos = tiempo_restante // 120
        mins     = segundos // 60
        segs     = segundos % 60
        color_t  = ROJO if segundos < 30 else CREMA
        # Parpadeo en los últimos 10 s
        if segundos < 10 and (tiempo_restante // 30) % 2 == 0:
            color_t = NEGRO
        timer_txt = self.f_grande.render(f"⏱ {mins:01d}:{segs:02d}", True, color_t)
        surface.blit(timer_txt, (ANCHO - timer_txt.get_width() - 20, 8))

        # Barra de tiempo
        barra_w = 200
        barra_x = ANCHO - barra_w - 20
        barra_y = 52
        frac    = tiempo_restante / max(tiempo_total, 1)
        col_b   = VERDE if frac > 0.5 else (AMARILLO if frac > 0.25 else ROJO)
        pygame.draw.rect(surface, GRIS_OSC, (barra_x, barra_y, barra_w, 12),
                         border_radius=6)
        pygame.draw.rect(surface, col_b,
                         (barra_x, barra_y, int(barra_w * frac), 12),
                         border_radius=6)

    # ── Banda inferior — cola de recetas ─────────────────────────────────────
    def _dibujar_banda_inferior(self, surface, recetas: list[Receta]):
        y0 = ALTO - HUD_ALTO_INF
        pygame.draw.rect(surface, NEGRO, (0, y0, ANCHO, HUD_ALTO_INF))
        pygame.draw.line(surface, NARANJA, (0, y0), (ANCHO, y0), 3)

        label = self.f_media.render("PEDIDOS:", True, CREMA)
        surface.blit(label, (10, y0 + 8))

        tarj_w = 160
        tarj_h = 70
        margen  = 8
        x       = 110

        for rec in recetas[:5]:   # máximo 5 en pantalla
            rect = pygame.Rect(x, y0 + 8, tarj_w, tarj_h)

            # Fondo tarjeta
            frac = rec.progreso_tiempo()
            col_borde = (VERDE if frac > 0.5 else
                         AMARILLO if frac > 0.25 else ROJO)
            pygame.draw.rect(surface, GRIS_OSC, rect, border_radius=6)
            pygame.draw.rect(surface, col_borde, rect, width=2, border_radius=6)

            # Nombre receta
            nom = self.f_small.render(rec.nombre, True, CREMA)
            surface.blit(nom, (rect.x + 4, rect.y + 4))

            # Puntos actuales
            pts = self.f_tiny.render(f"★ {rec.puntos_receta}", True, AMARILLO)
            surface.blit(pts, (rect.x + 4, rect.y + 20))

            # Ingredientes requeridos
            ings_txt = ", ".join(rec.nombres_requeridos)
            if len(ings_txt) > 22:
                ings_txt = ings_txt[:21] + "…"
            ing_surf = self.f_tiny.render(ings_txt, True, GRIS_MED)
            surface.blit(ing_surf, (rect.x + 4, rect.y + 34))

            # Barra de tiempo de la receta
            bw = tarj_w - 8
            pygame.draw.rect(surface, NEGRO,
                             (rect.x + 4, rect.bottom - 14, bw, 8),
                             border_radius=4)
            pygame.draw.rect(surface, col_borde,
                             (rect.x + 4, rect.bottom - 14,
                              int(bw * frac), 8),
                             border_radius=4)

            x += tarj_w + margen

    # ── Indicadores de chef ───────────────────────────────────────────────────
    def _dibujar_indicadores_chef(self, surface, chefs):
        colores = [(220, 80, 40), (40, 120, 220)]
        nombres = ["J1: WASD / Q", "J2: IJKL / U"]
        for i, chef in enumerate(chefs):
            x = 20 + i * 200
            y = HUD_ALTO_SUP + 8
            pygame.draw.circle(surface, colores[i], (x + 10, y + 10), 10)
            pygame.draw.circle(surface, BLANCO, (x + 10, y + 10), 10, 2)
            txt = self.f_tiny.render(nombres[i], True, colores[i])
            surface.blit(txt, (x + 24, y + 3))
            # Ingrediente en mano
            if chef.ingrediente_en_mano:
                ing = chef.ingrediente_en_mano
                col = VERDE if ing.esta_listo else (ROJO if ing.esta_quemado else CREMA)
                ing_txt = self.f_tiny.render(
                    f"→ {ing.nombre} [{ing.estado}]", True, col)
                surface.blit(ing_txt, (x + 24, y + 18))
