# menu.py — Pantalla de menú principal

import pygame
import math
from constantes import *


def _dibujar_fondo(surface, tick):
    surface.fill(CAFE_OSCURO)

    # Cuadrícula de fondo (estilo tablero de cocina)
    tam = 60
    offset = int(tick * 0.3) % tam
    for x in range(-tam, ANCHO + tam, tam):
        for y in range(-tam, ALTO + tam, tam):
            rx, ry = x + offset, y + offset
            if (x // tam + y // tam) % 2 == 0:
                pygame.draw.rect(surface, CAFE_MEDIO,
                                 (rx, ry, tam, tam))

    # Viñeta oscura en los bordes
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for i in range(120):
        alpha = int(180 * (i / 120) ** 2)
        pygame.draw.rect(overlay, (15, 12, 10, alpha),
                         (i, i, ANCHO - 2*i, ALTO - 2*i), 1)
    surface.blit(overlay, (0, 0))


def _dibujar_titulo(surface, fuente_grande, fuente_media, tick):
    """Título con efecto de parpadeo y sombra."""
    pulse = 0.05 * math.sin(tick * 0.04)
    escala = 1.0 + pulse

    # Sombra
    sombra = fuente_grande.render("CRAZY SNACK RUSH", True, NEGRO)
    sw = int(sombra.get_width() * escala)
    sh = int(sombra.get_height() * escala)
    sombra = pygame.transform.scale(sombra, (sw, sh))
    surface.blit(sombra, (ANCHO//2 - sw//2 + 5, 95))

    # Texto principal
    titulo1 = fuente_grande.render("CRAZY SNACK RUSH", True, NARANJA_VIV)
    w = int(titulo1.get_width() * escala)
    h = int(titulo1.get_height() * escala)
    titulo1 = pygame.transform.scale(titulo1, (w, h))
    surface.blit(titulo1, (ANCHO//2 - w//2, 90))



def _dibujar_botones(surface, fuente_btn, botones, hover_idx):
    """Dibuja los botones del menú."""
    for i, (label, rect) in enumerate(botones):
        es_hover = (i == hover_idx)

        # Sombra del botón
        sombra_rect = rect.inflate(6, 6).move(4, 4)
        pygame.draw.rect(surface, NEGRO, sombra_rect, border_radius=8)

        # Fondo del botón
        color_fondo = NARANJA_VIV if es_hover else NARANJA
        pygame.draw.rect(surface, color_fondo, rect, border_radius=8)

        # Borde
        color_borde = AMARILLO if es_hover else CAFE_MEDIO
        pygame.draw.rect(surface, color_borde, rect, width=3, border_radius=8)

        # Texto
        color_texto = NEGRO if es_hover else CREMA
        texto = fuente_btn.render(label, True, color_texto)
        surface.blit(texto, (rect.centerx - texto.get_width()//2,
                              rect.centery - texto.get_height()//2))


def _dibujar_decoraciones(surface, fuente_deco, tick):
    """Emojis/íconos decorativos animados."""
    iconos = ["🍳", "🔪", "🍕", "🍣", "⏱️"]
    for i, ic in enumerate(iconos):
        angulo = tick * 0.02 + i * (2 * math.pi / len(iconos))
        x = ANCHO//2 + int(380 * math.cos(angulo)) - 15
        y = ALTO//2  + int(220 * math.sin(angulo)) - 15
        # Sólo dibujar si está dentro de la pantalla
        if 0 < x < ANCHO - 40 and 0 < y < ALTO - 40:
            txt = fuente_deco.render(ic, True, AMARILLO)
            surface.blit(txt, (x, y))


class PantallaMenu:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.tick = 0
        self.hover_idx = -1

        # Fuentes
        pygame.font.init()
        self.fuente_grande = pygame.font.SysFont("impact", 64)
        self.fuente_media  = pygame.font.SysFont("impact", 28)
        self.fuente_btn    = pygame.font.SysFont("impact", 32)
        self.fuente_deco   = pygame.font.SysFont("segoeuiemoji", 28)

        # Definir botones centrados
        ancho_btn, alto_btn = 280, 55
        cx = ANCHO // 2
        self.botones = [
            (" JUGAR",   pygame.Rect(cx - ancho_btn//2, 260, ancho_btn, alto_btn)),
            ("OPCIONES", pygame.Rect(cx - ancho_btn//2, 330, ancho_btn, alto_btn)),
            ("SALIR",   pygame.Rect(cx - ancho_btn//2, 400, ancho_btn, alto_btn)),
        ]

    def manejar_evento(self, evento):
        """
        Retorna el nuevo estado si hubo clic, None si no.
        """
        if evento.type == pygame.MOUSEMOTION:
            mx, my = evento.pos
            self.hover_idx = -1
            for i, (_, rect) in enumerate(self.botones):
                if rect.collidepoint(mx, my):
                    self.hover_idx = i

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos
            for i, (label, rect) in enumerate(self.botones):
                if rect.collidepoint(mx, my):
                    if i == 0:
                        return ESTADO_SELECCION
                    elif i == 1:
                        return ESTADO_OPCIONES
                    elif i == 2:
                        return ESTADO_SALIR
        return None

    def actualizar(self):
        self.tick += 1

    def dibujar(self):
        _dibujar_fondo(self.pantalla, self.tick)
        _dibujar_titulo(self.pantalla, self.fuente_grande,
                        self.fuente_media, self.tick)
        _dibujar_botones(self.pantalla, self.fuente_btn,
                         self.botones, self.hover_idx)
        _dibujar_decoraciones(self.pantalla, self.fuente_deco, self.tick)
        