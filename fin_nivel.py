# fin_nivel.py — Pantalla de fin de nivel con resumen de puntuación

import pygame
import math
from constantes import *


class PantallaFinNivel:
    """
    Se muestra cuando el tiempo se agota.
    Presenta la puntuación final y botones para reintentar o volver al menú.
    """

    NOMBRES_ESC = ["Soda Tica", "Pizzería Roma", "Sushi Bar Kyoto"]   # Nombres por escenario
    ESTRELLAS_UMBRAL = [
        [0, 300, 600],    # Soda Tica          # Umbrales de puntos por estrella
        [0, 500, 900],    # Pizzería Roma
        [0, 700, 1200],   # Sushi Kyoto
    ]

    def __init__(self, pantalla: pygame.Surface,
                 escenario_idx: int, puntuacion: int):
        self.pantalla      = pantalla              # Superficie donde dibujar
        self.escenario_idx = escenario_idx          # Escenario jugado
        self.puntuacion    = puntuacion             # Puntos obtenidos
        self.tick          = 0                      # Contador de frames para animaciones

        umbrales = self.ESTRELLAS_UMBRAL[escenario_idx]   # Umbrales del escenario actual
        if puntuacion >= umbrales[2]:
            self.estrellas = 3                      # Puntaje máximo
        elif puntuacion >= umbrales[1]:
            self.estrellas = 2                      # Puntaje medio
        elif puntuacion >= umbrales[0]:
            self.estrellas = 1                      # Puntaje mínimo
        else:
            self.estrellas = 0                      # Sin estrellas

        self.f_titulo  = pygame.font.SysFont("impact", 52)         # Fuente título
        self.f_grande  = pygame.font.SysFont("impact", 38)         # Fuente texto grande
        self.f_media   = pygame.font.SysFont("impact", 26)         # Fuente texto medio
        self.f_emoji   = pygame.font.SysFont("segoeuiemoji", 40)   # Fuente para emojis

        cx = ANCHO // 2                                              # Centro horizontal de pantalla
        self.btn_reintentar = pygame.Rect(cx - 160, 430, 150, 50)   # Botón reintentar
        self.btn_menu       = pygame.Rect(cx + 10,  430, 150, 50)   # Botón volver al menú
        self.btn_siguiente  = pygame.Rect(cx - 75,  495, 150, 50)   # Botón siguiente escenario

        self._tiene_siguiente = escenario_idx < 2     # Si existe un escenario posterior

    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:   # Clic izquierdo
            mx, my = evento.pos                                            # Posición del clic
            if self.btn_reintentar.collidepoint(mx, my):
                return ESTADO_JUEGO          # vuelve a jugar el mismo      # Reinicia el mismo nivel
            if self.btn_menu.collidepoint(mx, my):
                return ESTADO_MENU                                          # Vuelve al menú principal
            if self._tiene_siguiente and self.btn_siguiente.collidepoint(mx, my):
                return ESTADO_SELECCION      # el jugador elige el siguiente   # Va a elegir escenario
        return None

    def actualizar(self):
        self.tick += 1     # Avanza el contador de animación

    def dibujar(self):
        self.pantalla.fill(CAFE_OSCURO)      # Pinta el fondo

        # Título animado
        pulse = 1.0 + 0.04 * math.sin(self.tick * 0.05)               # Factor de pulsación
        titulo_txt = "¡TIEMPO!" if self.puntuacion > 0 else "¡SIN PUNTOS!"   # Texto según resultado
        titulo_col = NARANJA_VIV if self.puntuacion > 0 else ROJO           # Color según resultado
        tit = self.f_titulo.render(titulo_txt, True, titulo_col)            # Renderiza el título
        w = int(tit.get_width() * pulse)                                    # Ancho escalado
        h = int(tit.get_height() * pulse)                                   # Alto escalado
        tit = pygame.transform.scale(tit, (w, h))                           # Aplica la escala
        self.pantalla.blit(tit, (ANCHO // 2 - w // 2, 60))                  # Dibuja centrado

        # Nombre del escenario
        nom = self.f_media.render(self.NOMBRES_ESC[self.escenario_idx],
                                   True, CREMA)                               # Nombre del restaurante
        self.pantalla.blit(nom, (ANCHO // 2 - nom.get_width() // 2, 145))   # Dibuja centrado

        # Puntuación
        pts = self.f_grande.render(f"Puntuación: {self.puntuacion}",
                                    True, AMARILLO)                          # Texto de puntuación
        self.pantalla.blit(pts, (ANCHO // 2 - pts.get_width() // 2, 200))  # Dibuja centrado

        # Estrellas
        estrellas_str = "⭐" * self.estrellas + "☆" * (3 - self.estrellas)  # Estrellas llenas/vacías
        star = self.f_emoji.render(estrellas_str, True, AMARILLO)            # Renderiza estrellas
        self.pantalla.blit(star, (ANCHO // 2 - star.get_width() // 2, 260)) # Dibuja centrado

        # Mensaje motivacional
        mensajes = {
            0: "¡Sigue practicando, chef!",     # Mensaje sin estrellas
            1: "¡Buen intento!",                # Mensaje con 1 estrella
            2: "¡Muy bien hecho!",               # Mensaje con 2 estrellas
            3: "¡Cocina perfecta!",              # Mensaje con 3 estrellas
        }
        msg = self.f_media.render(mensajes[self.estrellas], True, CREMA)    # Renderiza el mensaje
        self.pantalla.blit(msg, (ANCHO // 2 - msg.get_width() // 2, 330))  # Dibuja centrado

        # Separador
        pygame.draw.line(self.pantalla, NARANJA,
                         (100, 390), (ANCHO - 100, 390), 2)                 # Línea divisoria

        # Botones
        self._dibujar_btn(self.btn_reintentar, "↺ REINTENTAR", NARANJA)    # Botón de reintentar
        self._dibujar_btn(self.btn_menu,       "⌂ MENÚ",       GRIS_OSC)   # Botón de menú
        if self._tiene_siguiente:
            self._dibujar_btn(self.btn_siguiente, "→ SIGUIENTE", VERDE)    # Botón de siguiente nivel

    def _dibujar_btn(self, rect: pygame.Rect, texto: str, color: tuple):
        mx, my = pygame.mouse.get_pos()                                    # Posición actual del mouse
        hover  = rect.collidepoint(mx, my)                                 # Si el mouse está encima
        col    = tuple(min(255, c + 30) for c in color) if hover else color  # Aclara color si hay hover
        pygame.draw.rect(self.pantalla, col, rect, border_radius=8)        # Dibuja fondo del botón
        pygame.draw.rect(self.pantalla, AMARILLO if hover else GRIS_MED,
                         rect, width=2, border_radius=8)                   # Dibuja borde del botón
        txt = self.f_media.render(texto, True, NEGRO if hover else CREMA)  # Color de texto según hover
        self.pantalla.blit(txt, (rect.centerx - txt.get_width() // 2,      # Centrado horizontal
                                  rect.centery - txt.get_height() // 2))   # Centrado vertical
        