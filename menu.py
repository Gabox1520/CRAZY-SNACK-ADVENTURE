# menu.py — Pantalla de menú principal

import pygame
import math
from constantes import *


def _dibujar_fondo(surface, tick):
    surface.fill(CAFE_OSCURO)    # Pinta el fondo base

    # Cuadrícula de fondo (estilo tablero de cocina)
    tam = 60                                # Tamaño de cada cuadro
    offset = int(tick * 0.3) % tam          # Desplazamiento animado del patrón
    for x in range(-tam, ANCHO + tam, tam):       # Recorre columnas
        for y in range(-tam, ALTO + tam, tam):     # Recorre filas
            rx, ry = x + offset, y + offset         # Posición con desplazamiento
            if (x // tam + y // tam) % 2 == 0:      # Patrón tipo tablero de ajedrez
                pygame.draw.rect(surface, CAFE_MEDIO,
                                 (rx, ry, tam, tam))  # Dibuja el cuadro

    # Viñeta oscura en los bordes
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)   # Capa para la viñeta
    for i in range(120):                                        # Capas concéntricas
        alpha = int(180 * (i / 120) ** 2)                       # Transparencia progresiva
        pygame.draw.rect(overlay, (15, 12, 10, alpha),
                         (i, i, ANCHO - 2*i, ALTO - 2*i), 1)     # Dibuja el borde de la viñeta
    surface.blit(overlay, (0, 0))    # Aplica la viñeta sobre la pantalla


def _dibujar_titulo(surface, fuente_grande, fuente_media, tick):
    """Título con efecto de parpadeo y sombra."""
    pulse = 0.05 * math.sin(tick * 0.04)     # Factor de pulsación animada
    escala = 1.0 + pulse                      # Escala resultante

    # Sombra
    sombra = fuente_grande.render("CRAZY SNACK RUSH", True, NEGRO)    # Texto de sombra en negro
    sw = int(sombra.get_width() * escala)                              # Ancho escalado
    sh = int(sombra.get_height() * escala)                             # Alto escalado
    sombra = pygame.transform.scale(sombra, (sw, sh))                  # Aplica la escala
    surface.blit(sombra, (ANCHO//2 - sw//2 + 5, 95))                  # Dibuja con offset

    # Texto principal
    titulo1 = fuente_grande.render("CRAZY SNACK RUSH", True, NARANJA_VIV)  # Texto principal
    w = int(titulo1.get_width() * escala)                                  # Ancho escalado
    h = int(titulo1.get_height() * escala)                                 # Alto escalado
    titulo1 = pygame.transform.scale(titulo1, (w, h))                     # Aplica la escala
    surface.blit(titulo1, (ANCHO//2 - w//2, 90))                         # Dibuja centrado



def _dibujar_botones(surface, fuente_btn, botones, hover_idx):
    """Dibuja los botones del menú."""
    for i, (label, rect) in enumerate(botones):    # Recorre cada botón
        es_hover = (i == hover_idx)                 # Si el mouse está encima de este

        # Sombra del botón
        sombra_rect = rect.inflate(6, 6).move(4, 4)    # Rectángulo de sombra desplazado
        pygame.draw.rect(surface, NEGRO, sombra_rect, border_radius=8)   # Dibuja la sombra

        # Fondo del botón
        color_fondo = NARANJA_VIV if es_hover else NARANJA    # Color según hover
        pygame.draw.rect(surface, color_fondo, rect, border_radius=8)   # Dibuja el fondo

        # Borde
        color_borde = AMARILLO if es_hover else CAFE_MEDIO    # Color de borde según hover
        pygame.draw.rect(surface, color_borde, rect, width=3, border_radius=8)   # Dibuja el borde

        # Texto
        color_texto = NEGRO if es_hover else CREMA             # Color de texto según hover
        texto = fuente_btn.render(label, True, color_texto)     # Renderiza la etiqueta
        surface.blit(texto, (rect.centerx - texto.get_width()//2,   # Centrado horizontal
                              rect.centery - texto.get_height()//2)) # Centrado vertical


def _dibujar_decoraciones(surface, fuente_deco, tick):
    """Emojis/íconos decorativos animados."""
    iconos = ["🍳", "🔪", "🍕", "🍣", "⏱️"]    # Lista de emojis decorativos
    for i, ic in enumerate(iconos):                # Recorre cada emoji
        angulo = tick * 0.02 + i * (2 * math.pi / len(iconos))   # Ángulo de rotación animado
        x = ANCHO//2 + int(380 * math.cos(angulo)) - 15            # Posición x en círculo
        y = ALTO//2  + int(220 * math.sin(angulo)) - 15            # Posición y en círculo
        # Sólo dibujar si está dentro de la pantalla
        if 0 < x < ANCHO - 40 and 0 < y < ALTO - 40:
            txt = fuente_deco.render(ic, True, AMARILLO)            # Renderiza el ícono
            surface.blit(txt, (x, y))                                # Lo dibuja en pantalla


class PantallaMenu:
    def __init__(self, pantalla):
        self.pantalla = pantalla    # Superficie donde se dibuja
        self.tick = 0                # Contador de frames para animaciones
        self.hover_idx = -1          # Botón sobre el que está el mouse (-1 = ninguno)

        # Fuentes
        pygame.font.init()    # Inicializa el sistema de fuentes
        self.fuente_grande = pygame.font.SysFont("impact", 64)   # Fuente del título
        self.fuente_media  = pygame.font.SysFont("impact", 28)   # Fuente media (no usada directamente aquí)
        self.fuente_btn    = pygame.font.SysFont("impact", 32)   # Fuente de los botones
        self.fuente_deco   = pygame.font.SysFont("segoeuiemoji", 28)   # Fuente para emojis decorativos

        # Definir botones centrados
        ancho_btn, alto_btn = 280, 55    # Tamaño estándar de cada botón
        cx = ANCHO // 2                   # Centro horizontal de pantalla
        self.botones = [
            (" JUGAR",   pygame.Rect(cx - ancho_btn//2, 260, ancho_btn, alto_btn)),    # Botón jugar
            ("OPCIONES", pygame.Rect(cx - ancho_btn//2, 330, ancho_btn, alto_btn)),    # Botón opciones
            ("SALIR",   pygame.Rect(cx - ancho_btn//2, 400, ancho_btn, alto_btn)),    # Botón salir
        ]

    def manejar_evento(self, evento):
        """
        Retorna el nuevo estado si hubo clic, None si no.
        """
        if evento.type == pygame.MOUSEMOTION:        # Si el mouse se movió
            mx, my = evento.pos                        # Posición actual del mouse
            self.hover_idx = -1                         # Reinicia el índice de hover
            for i, (_, rect) in enumerate(self.botones):   # Revisa cada botón
                if rect.collidepoint(mx, my):                # Si el mouse está sobre él
                    self.hover_idx = i                         # Marca ese botón como hover

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:   # Clic izquierdo
            mx, my = evento.pos                                            # Posición del clic
            for i, (label, rect) in enumerate(self.botones):               # Revisa cada botón
                if rect.collidepoint(mx, my):                              # Si el clic fue sobre él
                    if i == 0:
                        return ESTADO_SELECCION     # Va a la pantalla de selección
                    elif i == 1:
                        return ESTADO_OPCIONES       # Va a la pantalla de opciones
                    elif i == 2:
                        return ESTADO_SALIR          # Sale del juego
        return None

    def actualizar(self):
        self.tick += 1    # Avanza el contador de animación

    def dibujar(self):
        _dibujar_fondo(self.pantalla, self.tick)                          # Dibuja el fondo animado
        _dibujar_titulo(self.pantalla, self.fuente_grande,
                        self.fuente_media, self.tick)                     # Dibuja el título
        _dibujar_botones(self.pantalla, self.fuente_btn,
                         self.botones, self.hover_idx)                    # Dibuja los botones
        _dibujar_decoraciones(self.pantalla, self.fuente_deco, self.tick) # Dibuja decoraciones
        