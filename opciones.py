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
        self.pantalla    = pantalla
        self.fullscreen  = False
        self.num_jugadores = 1

        self.volumen = audio.get_volumen()

        self.f_titulo = pygame.font.SysFont("impact", 42)
        self.f_label  = pygame.font.SysFont("impact", 26)
        self.f_valor  = pygame.font.SysFont("impact", 24)
        self.f_small  = pygame.font.SysFont("arial",  16)

        # Botón volver
        self.btn_volver = pygame.Rect(20, 20, 130, 38)

        # Slider de volumen
        self._slider_rect  = pygame.Rect(300, 200, 300, 16)
        self._slider_drag  = False

        # Botones jugadores
        self._btn_j1 = pygame.Rect(300, 290, 130, 44)
        self._btn_j2 = pygame.Rect(450, 290, 130, 44)

        # Botón pantalla completa
        self._btn_fs = pygame.Rect(300, 370, 280, 44)

        # Guardamos referencia al display para toggle FS
        self._flags_ventana = 0

    # ── Eventos ──────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos

            if self.btn_volver.collidepoint(mx, my):
                return ESTADO_MENU

            # Slider de volumen
            if self._slider_rect.collidepoint(mx, my):
                self._slider_drag = True
                self._actualizar_volumen(mx)

            # Botones jugadores
            if self._btn_j1.collidepoint(mx, my):
                self.num_jugadores = 1
            if self._btn_j2.collidepoint(mx, my):
                self.num_jugadores = 2

            # Pantalla completa
            if self._btn_fs.collidepoint(mx, my):
                self._toggle_fullscreen()

        if evento.type == pygame.MOUSEBUTTONUP:
            self._slider_drag = False

        if evento.type == pygame.MOUSEMOTION and self._slider_drag:
            self._actualizar_volumen(evento.pos[0])

        return None

    def _actualizar_volumen(self, mx: int):
        sx = self._slider_rect.x
        sw = self._slider_rect.width
        frac = max(0.0, min(1.0, (mx - sx) / sw))
        self.volumen = frac
        audio.set_volumen(frac)

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((ANCHO, ALTO))

    # ── Actualizar y dibujar ─────────────────────────────────────────────────
    def actualizar(self):
        pass

    def dibujar(self):
        self.pantalla.fill(CAFE_OSCURO)

        # Título
        tit = self.f_titulo.render("OPCIONES", True, NARANJA_VIV)
        self.pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 60))
        pygame.draw.line(self.pantalla, NARANJA,
                         (80, 115), (ANCHO - 80, 115), 2)

        # ── Volumen ──────────────────────────────────────────────────────────
        lbl = self.f_label.render("VOLUMEN:", True, CREMA)
        self.pantalla.blit(lbl, (100, 192))

        # Track del slider
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self._slider_rect, border_radius=8)
        # Relleno
        fill_w = int(self._slider_rect.width * self.volumen)
        fill_r = pygame.Rect(self._slider_rect.x, self._slider_rect.y,
                             fill_w, self._slider_rect.height)
        pygame.draw.rect(self.pantalla, NARANJA_VIV, fill_r, border_radius=8)
        pygame.draw.rect(self.pantalla, AMARILLO,
                         self._slider_rect, width=2, border_radius=8)
        # Handle
        hx = self._slider_rect.x + fill_w
        hy = self._slider_rect.centery
        pygame.draw.circle(self.pantalla, CREMA, (hx, hy), 10)
        pygame.draw.circle(self.pantalla, AMARILLO, (hx, hy), 10, 2)
        # Valor %
        pct = self.f_valor.render(f"{int(self.volumen * 100)}%", True, AMARILLO)
        self.pantalla.blit(pct, (self._slider_rect.right + 12, 192))

        # ── Jugadores ────────────────────────────────────────────────────────
        lbl2 = self.f_label.render("JUGADORES:", True, CREMA)
        self.pantalla.blit(lbl2, (100, 298))

        for n, btn in [(1, self._btn_j1), (2, self._btn_j2)]:
            activo = (self.num_jugadores == n)
            color  = NARANJA_VIV if activo else GRIS_OSC
            borde  = AMARILLO    if activo else GRIS_MED
            pygame.draw.rect(self.pantalla, color, btn, border_radius=8)
            pygame.draw.rect(self.pantalla, borde, btn, width=2, border_radius=8)
            txt = self.f_label.render(f"{n}P", True,
                                       NEGRO if activo else CREMA)
            self.pantalla.blit(txt, (btn.centerx - txt.get_width() // 2,
                                      btn.centery - txt.get_height() // 2))

        # ── Pantalla completa ─────────────────────────────────────────────────
        lbl3 = self.f_label.render("PANTALLA:", True, CREMA)
        self.pantalla.blit(lbl3, (100, 378))

        fs_color = NARANJA_VIV if self.fullscreen else GRIS_OSC
        fs_borde = AMARILLO    if self.fullscreen else GRIS_MED
        fs_label = "COMPLETA ✓" if self.fullscreen else "VENTANA"
        pygame.draw.rect(self.pantalla, fs_color,
                         self._btn_fs, border_radius=8)
        pygame.draw.rect(self.pantalla, fs_borde,
                         self._btn_fs, width=2, border_radius=8)
        fs_txt = self.f_label.render(fs_label, True,
                                      NEGRO if self.fullscreen else CREMA)
        self.pantalla.blit(fs_txt,
                           (self._btn_fs.centerx - fs_txt.get_width() // 2,
                            self._btn_fs.centery - fs_txt.get_height() // 2))

        # ── Controles (info) ──────────────────────────────────────────────────
        pygame.draw.line(self.pantalla, GRIS_MED,
                         (80, 445), (ANCHO - 80, 445), 1)
        controles = [
            "J1: WASD para mover | Q mantener = usar estación | E = acción 2",
            "J2: IJKL para mover | U mantener = usar estación | O = acción 2",
        ]
        for i, c in enumerate(controles):
            ct = self.f_small.render(c, True, GRIS_MED)
            self.pantalla.blit(ct, (ANCHO // 2 - ct.get_width() // 2,
                                    455 + i * 22))

        # ── Botón volver ──────────────────────────────────────────────────────
        pygame.draw.rect(self.pantalla, GRIS_OSC,
                         self.btn_volver, border_radius=7)
        pygame.draw.rect(self.pantalla, GRIS_MED,
                         self.btn_volver, width=2, border_radius=7)
        v = self.f_label.render("← VOLVER", True, CREMA)
        self.pantalla.blit(v, (self.btn_volver.centerx - v.get_width() // 2,
                                self.btn_volver.centery - v.get_height() // 2))
