# opciones.py — Pantalla de opciones: volumen, jugadores, pantalla completa

import pygame
from constantes import *
import audio


class PantallaOpciones:
    """
    Pantalla de opciones accesible desde el menú principal.
    Permite ajustar:
    - Volumen de música (barra deslizante)
    - Número de jugadores (1 o 2)
    - Modo pantalla completa
    """

    def __init__(self, pantalla: pygame.Surface):
        self.pantalla    = pantalla    # Superficie donde se dibuja
        self.fullscreen  = False        # Bandera de pantalla completa
        self.num_jugadores = 1          # Número de jugadores configurado

        self.volumen = audio.get_volumen()    # Volumen actual del sistema de audio

        self.f_titulo = pygame.font.SysFont("impact", 42)    # Fuente del título
        self.f_label  = pygame.font.SysFont("impact", 26)    # Fuente de etiquetas
        self.f_valor  = pygame.font.SysFont("impact", 24)    # Fuente de valores numéricos
        self.f_small  = pygame.font.SysFont("arial",  16)    # Fuente pequeña (controles)

        # Botón volver
        self.btn_volver = pygame.Rect(20, 20, 130, 38)    # Botón para volver al menú

        # Slider de volumen
        self._slider_rect  = pygame.Rect(300, 200, 300, 16)   # Barra deslizante de volumen
        self._slider_drag  = False                              # Si se está arrastrando el slider

        # Botones jugadores
        self._btn_j1 = pygame.Rect(300, 290, 130, 44)    # Botón "1 jugador"
        self._btn_j2 = pygame.Rect(450, 290, 130, 44)    # Botón "2 jugadores"

        # Botón pantalla completa
        self._btn_fs = pygame.Rect(300, 370, 280, 44)    # Botón de alternar pantalla completa

        # Guardamos referencia al display para toggle FS
        self._flags_ventana = 0    # (no usado actualmente, reservado)

    # ── Eventos ──────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:    # Clic izquierdo
            mx, my = evento.pos                                              # Posición del clic

            if self.btn_volver.collidepoint(mx, my):
                return ESTADO_MENU    # Vuelve al menú principal

            # Slider de volumen
            if self._slider_rect.collidepoint(mx, my):
                self._slider_drag = True                # Comienza a arrastrar el slider
                self._actualizar_volumen(mx)             # Ajusta el volumen según el clic

            # Botones jugadores
            if self._btn_j1.collidepoint(mx, my):
                self.num_jugadores = 1                    # Configura 1 jugador
            if self._btn_j2.collidepoint(mx, my):
                self.num_jugadores = 2                    # Configura 2 jugadores

            # Pantalla completa
            if self._btn_fs.collidepoint(mx, my):
                self._toggle_fullscreen()                  # Alterna pantalla completa

        if evento.type == pygame.MOUSEBUTTONUP:
            self._slider_drag = False    # Termina el arrastre del slider

        if evento.type == pygame.MOUSEMOTION and self._slider_drag:
            self._actualizar_volumen(evento.pos[0])    # Sigue ajustando mientras se arrastra

        return None

    def _actualizar_volumen(self, mx: int):
        sx = self._slider_rect.x                          # Posición x inicial del slider
        sw = self._slider_rect.width                       # Ancho total del slider
        frac = max(0.0, min(1.0, (mx - sx) / sw))          # Fracción de posición (0.0 a 1.0)
        self.volumen = frac                                 # Actualiza el volumen interno
        audio.set_volumen(frac)                             # Aplica el volumen al sistema de audio

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen    # Invierte la bandera
        if self.fullscreen:
            pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)   # Activa pantalla completa
        else:
            pygame.display.set_mode((ANCHO, ALTO))                       # Vuelve a modo ventana

    # ── Actualizar y dibujar ─────────────────────────────────────────────────
    def actualizar(self):
        pass    # Esta pantalla no requiere lógica por frame

    def dibujar(self):
        self.pantalla.fill(CAFE_OSCURO)    # Pinta el fondo

        # Título
        tit = self.f_titulo.render("OPCIONES", True, NARANJA_VIV)    # Texto del título
        self.pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 60))   # Dibuja centrado
        pygame.draw.line(self.pantalla, NARANJA,
                         (80, 115), (ANCHO - 80, 115), 2)             # Línea separadora

        # ── Volumen ──────────────────────────────────────────────────────────
        lbl = self.f_label.render("VOLUMEN:", True, CREMA)            # Etiqueta de volumen
        self.pantalla.blit(lbl, (100, 192))                            # Dibuja la etiqueta

        # Track del slider
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self._slider_rect, border_radius=8)          # Fondo de la barra
        # Relleno
        fill_w = int(self._slider_rect.width * self.volumen)          # Ancho del relleno según volumen
        fill_r = pygame.Rect(self._slider_rect.x, self._slider_rect.y,
                             fill_w, self._slider_rect.height)         # Rectángulo del relleno
        pygame.draw.rect(self.pantalla, NARANJA_VIV, fill_r, border_radius=8)   # Dibuja el relleno
        pygame.draw.rect(self.pantalla, AMARILLO,
                         self._slider_rect, width=2, border_radius=8) # Borde de la barra
        # Handle
        hx = self._slider_rect.x + fill_w                              # Posición x del control deslizante
        hy = self._slider_rect.centery                                  # Posición y del control deslizante
        pygame.draw.circle(self.pantalla, CREMA, (hx, hy), 10)         # Círculo del control
        pygame.draw.circle(self.pantalla, AMARILLO, (hx, hy), 10, 2)   # Borde del control
        # Valor %
        pct = self.f_valor.render(f"{int(self.volumen * 100)}%", True, AMARILLO)   # Texto de porcentaje
        self.pantalla.blit(pct, (self._slider_rect.right + 12, 192))   # Dibuja junto al slider

        # ── Jugadores ────────────────────────────────────────────────────────
        lbl2 = self.f_label.render("JUGADORES:", True, CREMA)          # Etiqueta de jugadores
        self.pantalla.blit(lbl2, (100, 298))                            # Dibuja la etiqueta

        for n, btn in [(1, self._btn_j1), (2, self._btn_j2)]:           # Por cada opción de jugadores
            activo = (self.num_jugadores == n)                          # Si es la opción seleccionada
            color  = NARANJA_VIV if activo else GRIS_OSC                # Color de fondo según selección
            borde  = AMARILLO    if activo else GRIS_MED                # Color de borde según selección
            pygame.draw.rect(self.pantalla, color, btn, border_radius=8)   # Dibuja el fondo del botón
            pygame.draw.rect(self.pantalla, borde, btn, width=2, border_radius=8)  # Dibuja el borde
            txt = self.f_label.render(f"{n}P", True,
                                       NEGRO if activo else CREMA)       # Texto "1P" o "2P"
            self.pantalla.blit(txt, (btn.centerx - txt.get_width() // 2,   # Centrado horizontal
                                      btn.centery - txt.get_height() // 2)) # Centrado vertical

        # ── Pantalla completa ─────────────────────────────────────────────────
        lbl3 = self.f_label.render("PANTALLA:", True, CREMA)            # Etiqueta de pantalla
        self.pantalla.blit(lbl3, (100, 378))                             # Dibuja la etiqueta

        fs_color = NARANJA_VIV if self.fullscreen else GRIS_OSC          # Color de fondo según estado
        fs_borde = AMARILLO    if self.fullscreen else GRIS_MED          # Color de borde según estado
        fs_label = "COMPLETA ✓" if self.fullscreen else "VENTANA"        # Texto según estado
        pygame.draw.rect(self.pantalla, fs_color,
                         self._btn_fs, border_radius=8)                 # Dibuja el fondo del botón
        pygame.draw.rect(self.pantalla, fs_borde,
                         self._btn_fs, width=2, border_radius=8)        # Dibuja el borde
        fs_txt = self.f_label.render(fs_label, True,
                                      NEGRO if self.fullscreen else CREMA)  # Texto del botón
        self.pantalla.blit(fs_txt,
                           (self._btn_fs.centerx - fs_txt.get_width() // 2,   # Centrado horizontal
                            self._btn_fs.centery - fs_txt.get_height() // 2)) # Centrado vertical

        # ── Controles (info) ──────────────────────────────────────────────────
        pygame.draw.line(self.pantalla, GRIS_MED,
                         (80, 445), (ANCHO - 80, 445), 1)               # Línea separadora
        controles = [
            "J1: WASD para mover | Q mantener = usar estación | E = acción 2",   # Controles jugador 1
            "J2: IJKL para mover | U mantener = usar estación | O = acción 2",   # Controles jugador 2
        ]
        for i, c in enumerate(controles):                               # Por cada línea de controles
            ct = self.f_small.render(c, True, GRIS_MED)                  # Renderiza el texto
            self.pantalla.blit(ct, (ANCHO // 2 - ct.get_width() // 2,    # Centrado horizontal
                                    455 + i * 22))                        # Posición vertical según línea

        # ── Botón volver ──────────────────────────────────────────────────────
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self.btn_volver, border_radius=7)              # Fondo del botón volver
        pygame.draw.rect(self.pantalla, GRIS_MED,
                         self.btn_volver, width=2, border_radius=7)     # Borde del botón volver
        v = self.f_label.render("← VOLVER", True, CREMA)                 # Texto del botón
        self.pantalla.blit(v, (self.btn_volver.centerx - v.get_width() // 2,   # Centrado horizontal
                                self.btn_volver.centery - v.get_height() // 2)) # Centrado vertical
        