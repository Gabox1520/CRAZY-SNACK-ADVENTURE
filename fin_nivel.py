# fin_nivel.py — Pantalla de fin de nivel con resumen de puntuación

import pygame
import math
from constantes import *


class PantallaFinNivel:
    """
    Se muestra cuando el tiempo se agota.
    Presenta la puntuación final y botones para reintentar o volver al menú.
    """

    NOMBRES_ESC = ["Soda Tica", "Pizzería Roma", "Sushi Bar Kyoto"]
    ESTRELLAS_UMBRAL = [
        [0, 300, 600],    # Soda Tica
        [0, 500, 900],    # Pizzería Roma
        [0, 700, 1200],   # Sushi Kyoto
    ]

    def __init__(self, pantalla: pygame.Surface,
                 escenario_idx: int, puntuacion: int):
        self.pantalla      = pantalla
        self.escenario_idx = escenario_idx
        self.puntuacion    = puntuacion
        self.tick          = 0

        umbrales = self.ESTRELLAS_UMBRAL[escenario_idx]
        if puntuacion >= umbrales[2]:
            self.estrellas = 3
        elif puntuacion >= umbrales[1]:
            self.estrellas = 2
        elif puntuacion >= umbrales[0]:
            self.estrellas = 1
        else:
            self.estrellas = 0

        self.f_titulo  = pygame.font.SysFont("impact", 52)
        self.f_grande  = pygame.font.SysFont("impact", 38)
        self.f_media   = pygame.font.SysFont("impact", 26)
        self.f_emoji   = pygame.font.SysFont("segoeuiemoji", 40)

        cx = ANCHO // 2
        self.btn_reintentar = pygame.Rect(cx - 160, 430, 150, 50)
        self.btn_menu       = pygame.Rect(cx + 10,  430, 150, 50)
        self.btn_siguiente  = pygame.Rect(cx - 75,  495, 150, 50)

        self._tiene_siguiente = escenario_idx < 2

    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos
            if self.btn_reintentar.collidepoint(mx, my):
                return ESTADO_JUEGO          # vuelve a jugar el mismo
            if self.btn_menu.collidepoint(mx, my):
                return ESTADO_MENU
            if self._tiene_siguiente and self.btn_siguiente.collidepoint(mx, my):
                return ESTADO_SELECCION      # el jugador elige el siguiente
        return None

    def actualizar(self):
        self.tick += 1

    def dibujar(self):
        self.pantalla.fill(CAFE_OSCURO)

        # Título animado
        pulse = 1.0 + 0.04 * math.sin(self.tick * 0.05)
        titulo_txt = "¡TIEMPO!" if self.puntuacion > 0 else "¡SIN PUNTOS!"
        titulo_col = NARANJA_VIV if self.puntuacion > 0 else ROJO
        tit = self.f_titulo.render(titulo_txt, True, titulo_col)
        w = int(tit.get_width() * pulse)
        h = int(tit.get_height() * pulse)
        tit = pygame.transform.scale(tit, (w, h))
        self.pantalla.blit(tit, (ANCHO // 2 - w // 2, 60))

        # Nombre del escenario
        nom = self.f_media.render(self.NOMBRES_ESC[self.escenario_idx],
                                   True, CREMA)
        self.pantalla.blit(nom, (ANCHO // 2 - nom.get_width() // 2, 145))

        # Puntuación
        pts = self.f_grande.render(f"Puntuación: {self.puntuacion}",
                                    True, AMARILLO)
        self.pantalla.blit(pts, (ANCHO // 2 - pts.get_width() // 2, 200))

        # Estrellas
        estrellas_str = "⭐" * self.estrellas + "☆" * (3 - self.estrellas)
        star = self.f_emoji.render(estrellas_str, True, AMARILLO)
        self.pantalla.blit(star, (ANCHO // 2 - star.get_width() // 2, 260))

        # Mensaje motivacional
        mensajes = {
            0: "¡Sigue practicando, chef!",
            1: "¡Buen intento!",
            2: "¡Muy bien hecho!",
            3: "¡Cocina perfecta!",
        }
        msg = self.f_media.render(mensajes[self.estrellas], True, CREMA)
        self.pantalla.blit(msg, (ANCHO // 2 - msg.get_width() // 2, 330))

        # Separador
        pygame.draw.line(self.pantalla, NARANJA,
                         (100, 390), (ANCHO - 100, 390), 2)

        # Botones
        self._dibujar_btn(self.btn_reintentar, "↺ REINTENTAR", NARANJA)
        self._dibujar_btn(self.btn_menu,       "⌂ MENÚ",       GRIS_OSC)
        if self._tiene_siguiente:
            self._dibujar_btn(self.btn_siguiente, "→ SIGUIENTE", VERDE)

    def _dibujar_btn(self, rect: pygame.Rect, texto: str, color: tuple):
        mx, my = pygame.mouse.get_pos()
        hover  = rect.collidepoint(mx, my)
        col    = tuple(min(255, c + 30) for c in color) if hover else color
        pygame.draw.rect(self.pantalla, col, rect, border_radius=8)
        pygame.draw.rect(self.pantalla, AMARILLO if hover else GRIS_MED,
                         rect, width=2, border_radius=8)
        txt = self.f_media.render(texto, True, NEGRO if hover else CREMA)
        self.pantalla.blit(txt, (rect.centerx - txt.get_width() // 2,
                                  rect.centery - txt.get_height() // 2))
