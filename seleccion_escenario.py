# seleccion_escenario.py — Pantalla de selección de restaurante

import pygame
import math
from constantes import *

# Datos de los tres escenarios
ESCENARIOS = [
    {
        "nombre":      "Soda Tica",                                          # Nombre del restaurante
        "dificultad":  "Fácil",                                              # Nivel de dificultad
        "descripcion": ["Recetas caseras costarricenses.", "Gallo pinto y casado."],  # Texto descriptivo
        "emoji":       "🫘",                                                  # Ícono representativo
        "color":       (200, 90, 30),                                        # Color principal
        "color2":      (240, 140, 50),                                       # Color secundario
        "recetas":     ["Gallo Pinto", "Casado"],                            # Recetas disponibles
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
    "Fácil":  VERDE,      # Color para dificultad fácil
    "Medio":  AMARILLO,   # Color para dificultad media
    "Difícil": ROJO,      # Color para dificultad difícil
}


def _dibujar_fondo_seleccion(surface):
    surface.fill(CAFE_OSCURO)    # Pinta el fondo base
    # Líneas horizontales decorativas
    for y in range(0, ALTO, 40):                          # Recorre posiciones verticales
        pygame.draw.line(surface, CAFE_MEDIO, (0, y), (ANCHO, y), 1)   # Dibuja línea horizontal


def _dibujar_tarjeta(surface, fuentes, escenario, rect, hover, tick):
    col  = escenario["color"]      # Color principal del escenario
    col2 = escenario["color2"]     # Color secundario del escenario

    # Sombra
    sombra = rect.inflate(8, 8).move(5, 5)                          # Rectángulo de sombra desplazado
    pygame.draw.rect(surface, NEGRO, sombra, border_radius=14)      # Dibuja la sombra

    # Fondo de la tarjeta
    if hover:
        # Gradiente simulado con dos rectángulos
        mitad = rect.copy()                          # Copia del rectángulo
        mitad.height = rect.height // 2                # Solo la mitad superior
        pygame.draw.rect(surface, col2, rect, border_radius=14)    # Fondo completo con color2
        pygame.draw.rect(surface, col,  mitad, border_radius=14)   # Mitad superior con color principal
    else:
        pygame.draw.rect(surface, GRIS_OSC, rect, border_radius=14)   # Fondo neutro sin hover

    # Borde
    color_borde = AMARILLO if hover else GRIS_MED          # Color de borde según hover
    grosor_borde = 3 if hover else 2                        # Grosor de borde según hover
    pygame.draw.rect(surface, color_borde, rect,
                     width=grosor_borde, border_radius=14)  # Dibuja el borde

    # Emoji grande
    bounce = int(6 * math.sin(tick * 0.05)) if hover else 0     # Animación de rebote si hay hover
    emoji_txt = fuentes["emoji"].render(escenario["emoji"], True, CREMA)   # Renderiza el emoji
    surface.blit(emoji_txt, (rect.centerx - emoji_txt.get_width()//2,     # Centrado horizontal
                              rect.top + 18 + bounce))                     # Posición con rebote

    # Nombre
    nombre = fuentes["titulo"].render(escenario["nombre"], True,
                                      CREMA if not hover else AMARILLO)    # Color según hover
    surface.blit(nombre, (rect.centerx - nombre.get_width()//2,            # Centrado horizontal
                           rect.top + 90))                                  # Posición fija

    # Dificultad
    color_dif = COLORES_DIFICULTAD[escenario["dificultad"]]                # Color según dificultad
    dif_surf = fuentes["dif"].render(
        f"◆ {escenario['dificultad']}", True, color_dif)                   # Texto de dificultad
    surface.blit(dif_surf, (rect.centerx - dif_surf.get_width()//2,        # Centrado horizontal
                             rect.top + 125))                               # Posición fija

    # Separador
    pygame.draw.line(surface, GRIS_MED,
                     (rect.left + 20, rect.top + 152),
                     (rect.right - 20, rect.top + 152), 1)                  # Línea divisoria

    # Descripción
    for i, linea in enumerate(escenario["descripcion"]):                    # Por cada línea de texto
        desc = fuentes["desc"].render(linea, True, CREMA)                    # Renderiza la línea
        surface.blit(desc, (rect.centerx - desc.get_width()//2,             # Centrado horizontal
                             rect.top + 162 + i * 22))                       # Posición según línea

    # Lista de recetas
    y_rec = rect.top + 215                                                    # Posición y inicial
    for rec in escenario["recetas"]:                                          # Por cada receta del escenario
        r_surf = fuentes["rec"].render(f"• {rec}", True,
                                       AMARILLO if hover else GRIS_MED)        # Color según hover
        surface.blit(r_surf, (rect.left + 22, y_rec))                         # Dibuja la receta
        y_rec += 20                                                            # Avanza posición vertical

    # Botón de selección al hover
    if hover:
        btn_rect = pygame.Rect(rect.left + 20, rect.bottom - 52,
                               rect.width - 40, 36)                            # Rectángulo del botón
        pygame.draw.rect(surface, AMARILLO, btn_rect, border_radius=7)        # Fondo del botón
        btn_txt = fuentes["btn"].render("SELECCIONAR", True, NEGRO)            # Texto del botón
        surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2,     # Centrado horizontal
                                btn_rect.centery - btn_txt.get_height()//2))   # Centrado vertical


class PantallaSeleccion:
    def __init__(self, pantalla):
        self.pantalla = pantalla       # Superficie donde se dibuja
        self.tick = 0                   # Contador de frames para animaciones
        self.hover_idx = -1             # Tarjeta sobre la que está el mouse
        self.escenario_elegido = None  # índice 0/1/2     # Escenario seleccionado por el jugador

        # Fuentes
        self.fuentes = {
            "titulo": pygame.font.SysFont("impact", 22),     # Fuente del nombre del restaurante
            "dif":    pygame.font.SysFont("impact", 18),     # Fuente de la dificultad
            "desc":   pygame.font.SysFont("arial", 15),      # Fuente de la descripción
            "rec":    pygame.font.SysFont("arial", 14),      # Fuente de la lista de recetas
            "btn":    pygame.font.SysFont("impact", 18),     # Fuente del botón seleccionar
            "emoji":  pygame.font.SysFont("segoeuiemoji", 42),  # Fuente para el emoji
            "header": pygame.font.SysFont("impact", 38),     # Fuente del encabezado
            "volver": pygame.font.SysFont("impact", 22),      # Fuente del botón volver
        }

        # Tarjetas: 3 columnas centradas
        margen_lat = 50                                          # Margen lateral de las tarjetas
        espacio    = 20                                          # Espacio entre tarjetas
        ancho_tarj = (ANCHO - 2*margen_lat - 2*espacio) // 3      # Ancho calculado de cada tarjeta
        alto_tarj  = 360                                          # Alto fijo de cada tarjeta
        y_tarj     = 130                                          # Posición vertical de las tarjetas

        self.rects = []
        for i in range(3):                                        # Por cada una de las 3 tarjetas
            x = margen_lat + i * (ancho_tarj + espacio)            # Posición x de la tarjeta
            self.rects.append(pygame.Rect(x, y_tarj, ancho_tarj, alto_tarj))   # Guarda el rectángulo

        # Botón volver
        self.btn_volver = pygame.Rect(20, 20, 120, 38)    # Botón para volver al menú

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEMOTION:                # Si el mouse se movió
            mx, my = evento.pos                                 # Posición actual del mouse
            self.hover_idx = -1                                  # Reinicia el índice de hover
            for i, rect in enumerate(self.rects):                # Revisa cada tarjeta
                if rect.collidepoint(mx, my):                       # Si el mouse está sobre ella
                    self.hover_idx = i                               # Marca esa tarjeta como hover

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:   # Clic izquierdo
            mx, my = evento.pos                                            # Posición del clic
            # Volver al menú
            if self.btn_volver.collidepoint(mx, my):
                return ESTADO_MENU                                          # Vuelve al menú principal
            # Seleccionar escenario
            for i, rect in enumerate(self.rects):                          # Revisa cada tarjeta
                if rect.collidepoint(mx, my):                               # Si el clic fue sobre ella
                    self.escenario_elegido = i                              # Guarda el escenario elegido
                    return ESTADO_JUEGO                                      # Inicia la partida
        return None

    def actualizar(self):
        self.tick += 1    # Avanza el contador de animación

    def dibujar(self):
        _dibujar_fondo_seleccion(self.pantalla)    # Dibuja el fondo

        # Header
        header = self.fuentes["header"].render(
            "SELECCIONA TU RESTAURANTE", True, NARANJA_VIV)    # Texto del encabezado
        self.pantalla.blit(header,
                           (ANCHO//2 - header.get_width()//2, 68))   # Dibuja centrado

        # Línea bajo el header
        pygame.draw.line(self.pantalla, NARANJA,
                         (80, 112), (ANCHO - 80, 112), 2)             # Línea divisoria

        # Tarjetas
        for i, (esc, rect) in enumerate(zip(ESCENARIOS, self.rects)):   # Por cada escenario
            _dibujar_tarjeta(self.pantalla, self.fuentes, esc, rect,
                             self.hover_idx == i, self.tick)             # Dibuja su tarjeta

        # Botón volver
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self.btn_volver, border_radius=7)             # Fondo del botón
        pygame.draw.rect(self.pantalla, GRIS_MED,
                         self.btn_volver, width=2, border_radius=7)    # Borde del botón
        v_txt = self.fuentes["volver"].render("← VOLVER", True, CREMA)   # Texto del botón
        self.pantalla.blit(v_txt, (
            self.btn_volver.centerx - v_txt.get_width()//2,             # Centrado horizontal
            self.btn_volver.centery - v_txt.get_height()//2))           # Centrado vertical
        