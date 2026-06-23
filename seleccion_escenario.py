# seleccion_escenario.py — Pantalla de selección de restaurante

import pygame
import math
from constantes import *

# Datos de los tres escenarios
ESCENARIOS = [
    {
        "nombre":      "Soda Tica",
        "dificultad":  "Fácil",
        "descripcion": ["Recetas caseras costarricenses.", "Gallo pinto y casado."],
        "emoji":       "🫘",
        "color":       (200, 90, 30),
        "color2":      (240, 140, 50),
        "recetas":     ["Gallo Pinto", "Casado"],
    },
    {
        "nombre":      "Pizzería Roma",
        "dificultad":  "Medio",
        "descripcion": ["Sabores italianos bajo presión.", "Masas, salsas y quesos."],
        "emoji":       "🍕",
        "color":       (180, 40, 40),
        "color2":      (220, 80, 60),
        "recetas":     ["Margarita", "Pepperoni", "Calzone"],
    },
    {
        "nombre":      "Sushi Bar Kyoto",
        "dificultad":  "Difícil",
        "descripcion": ["Precisión y velocidad japonesa.", "Rolls, nigiris y más."],
        "emoji":       "🍣",
        "color":       (30, 80, 160),
        "color2":      (60, 130, 200),
        "recetas":     ["California Roll", "Nigiri", "Temaki", "Miso Soup"],
    },
]

COLORES_DIFICULTAD = {
    "Fácil":  VERDE,
    "Medio":  AMARILLO,
    "Difícil": ROJO,
}


def _dibujar_fondo_seleccion(surface):
    surface.fill(CAFE_OSCURO)
    # Líneas horizontales decorativas
    for y in range(0, ALTO, 40):
        pygame.draw.line(surface, CAFE_MEDIO, (0, y), (ANCHO, y), 1)


def _dibujar_tarjeta(surface, fuentes, escenario, rect, hover, tick):
    col  = escenario["color"]
    col2 = escenario["color2"]

    # Sombra
    sombra = rect.inflate(8, 8).move(5, 5)
    pygame.draw.rect(surface, NEGRO, sombra, border_radius=14)

    # Fondo de la tarjeta
    if hover:
        # Gradiente simulado con dos rectángulos
        mitad = rect.copy()
        mitad.height = rect.height // 2
        pygame.draw.rect(surface, col2, rect, border_radius=14)
        pygame.draw.rect(surface, col,  mitad, border_radius=14)
    else:
        pygame.draw.rect(surface, GRIS_OSC, rect, border_radius=14)

    # Borde
    color_borde = AMARILLO if hover else GRIS_MED
    grosor_borde = 3 if hover else 2
    pygame.draw.rect(surface, color_borde, rect,
                     width=grosor_borde, border_radius=14)

    # Emoji grande
    bounce = int(6 * math.sin(tick * 0.05)) if hover else 0
    emoji_txt = fuentes["emoji"].render(escenario["emoji"], True, CREMA)
    surface.blit(emoji_txt, (rect.centerx - emoji_txt.get_width()//2,
                              rect.top + 18 + bounce))

    # Nombre
    nombre = fuentes["titulo"].render(escenario["nombre"], True,
                                      CREMA if not hover else AMARILLO)
    surface.blit(nombre, (rect.centerx - nombre.get_width()//2,
                           rect.top + 90))

    # Dificultad
    color_dif = COLORES_DIFICULTAD[escenario["dificultad"]]
    dif_surf = fuentes["dif"].render(
        f"◆ {escenario['dificultad']}", True, color_dif)
    surface.blit(dif_surf, (rect.centerx - dif_surf.get_width()//2,
                             rect.top + 125))

    # Separador
    pygame.draw.line(surface, GRIS_MED,
                     (rect.left + 20, rect.top + 152),
                     (rect.right - 20, rect.top + 152), 1)

    # Descripción
    for i, linea in enumerate(escenario["descripcion"]):
        desc = fuentes["desc"].render(linea, True, CREMA)
        surface.blit(desc, (rect.centerx - desc.get_width()//2,
                             rect.top + 162 + i * 22))

    # Lista de recetas
    y_rec = rect.top + 215
    for rec in escenario["recetas"]:
        r_surf = fuentes["rec"].render(f"• {rec}", True,
                                       AMARILLO if hover else GRIS_MED)
        surface.blit(r_surf, (rect.left + 22, y_rec))
        y_rec += 20

    # Botón de selección al hover
    if hover:
        btn_rect = pygame.Rect(rect.left + 20, rect.bottom - 52,
                               rect.width - 40, 36)
        pygame.draw.rect(surface, AMARILLO, btn_rect, border_radius=7)
        btn_txt = fuentes["btn"].render("SELECCIONAR", True, NEGRO)
        surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2,
                                btn_rect.centery - btn_txt.get_height()//2))


class PantallaSeleccion:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.tick = 0
        self.hover_idx = -1
        self.escenario_elegido = None  # índice 0/1/2

        # Fuentes
        self.fuentes = {
            "titulo": pygame.font.SysFont("impact", 22),
            "dif":    pygame.font.SysFont("impact", 18),
            "desc":   pygame.font.SysFont("arial", 15),
            "rec":    pygame.font.SysFont("arial", 14),
            "btn":    pygame.font.SysFont("impact", 18),
            "emoji":  pygame.font.SysFont("segoeuiemoji", 42),
            "header": pygame.font.SysFont("impact", 38),
            "volver": pygame.font.SysFont("impact", 22),
        }

        # Tarjetas: 3 columnas centradas
        margen_lat = 50
        espacio    = 20
        ancho_tarj = (ANCHO - 2*margen_lat - 2*espacio) // 3
        alto_tarj  = 360
        y_tarj     = 130

        self.rects = []
        for i in range(3):
            x = margen_lat + i * (ancho_tarj + espacio)
            self.rects.append(pygame.Rect(x, y_tarj, ancho_tarj, alto_tarj))

        # Botón volver
        self.btn_volver = pygame.Rect(20, 20, 120, 38)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            mx, my = evento.pos
            self.hover_idx = -1
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(mx, my):
                    self.hover_idx = i

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos
            # Volver al menú
            if self.btn_volver.collidepoint(mx, my):
                return ESTADO_MENU
            # Seleccionar escenario
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(mx, my):
                    self.escenario_elegido = i
                    return ESTADO_JUEGO
        return None

    def actualizar(self):
        self.tick += 1

    def dibujar(self):
        _dibujar_fondo_seleccion(self.pantalla)

        # Header
        header = self.fuentes["header"].render(
            "SELECCIONA TU RESTAURANTE", True, NARANJA_VIV)
        self.pantalla.blit(header,
                           (ANCHO//2 - header.get_width()//2, 68))

        # Línea bajo el header
        pygame.draw.line(self.pantalla, NARANJA,
                         (80, 112), (ANCHO - 80, 112), 2)

        # Tarjetas
        for i, (esc, rect) in enumerate(zip(ESCENARIOS, self.rects)):
            _dibujar_tarjeta(self.pantalla, self.fuentes, esc, rect,
                             self.hover_idx == i, self.tick)

        # Botón volver
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self.btn_volver, border_radius=7)
        pygame.draw.rect(self.pantalla, GRIS_MED,
                         self.btn_volver, width=2, border_radius=7)
        v_txt = self.fuentes["volver"].render("← VOLVER", True, CREMA)
        self.pantalla.blit(v_txt, (
            self.btn_volver.centerx - v_txt.get_width()//2,
            self.btn_volver.centery - v_txt.get_height()//2))
