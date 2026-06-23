# chef.py — Clase Chef con movimiento en grilla e interacción con estaciones

import pygame
from constantes import *
from ingredientes import Ingrediente
from estaciones import (Estacion, TablaCortar, EstacionCocina,
                        Freidora, Mostrador, EstacionEntrega, Despensa)

TAM_CELDA = 60   # píxeles por celda (debe coincidir con el mapa)

# Dirección → (dfila, dcol)
DIRS = {
    'up':    (-1,  0),
    'down':  ( 1,  0),
    'left':  ( 0, -1),
    'right': ( 0,  1),
}


class Chef:
    """
    Personaje jugable. Se mueve en una grilla y puede:
    - Recoger/soltar ingredientes de las estaciones
    - Procesar ingredientes manteniéndose en la estación
    """

    COLORES = [
        (220, 80,  40),   # Chef 1 — naranja
        (40,  120, 220),  # Chef 2 — azul
    ]
    COLORES_BORDE = [
        (255, 160, 80),
        (100, 180, 255),
    ]

    def __init__(self, jugador_idx: int, fila: int, col: int,
                 teclas: dict, tam_celda: int = TAM_CELDA):
        self.jugador_idx = jugador_idx
        self.fila = fila
        self.col  = col
        self.tam  = tam_celda

        # Teclas: {'up', 'down', 'left', 'right', 'accion1', 'accion2'}
        self.teclas = teclas

        self.ingrediente_en_mano: Ingrediente | None = None
        self.direccion = 'down'

        # Movimiento con delay para no moverse 120 veces por segundo
        self._move_delay   = 8    # frames entre pasos
        self._move_counter = 0

        # Referencia a la estación activa (procesando)
        self._estacion_activa: Estacion | None = None

        # Inventario acumulado para entrega (lista de hasta 3 ings)
        self.inventario: list[Ingrediente] = []

        # Offset de dibujo (posición en píxeles, para smooth visual)
        self.px = 0
        self.py = 0

        self.color       = self.COLORES[jugador_idx]
        self.color_borde = self.COLORES_BORDE[jugador_idx]

    # ── Input ────────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event,
                       grid: list[list], offset_x: int, offset_y: int):
        """
        Procesa eventos de teclado del jugador.
        grid: matriz 2D de Estacion|None
        """
        if evento.type == pygame.KEYDOWN:
            # Acción principal — recoger/usar estación
            if evento.key == self.teclas['accion1']:
                self._accion(grid, offset_x, offset_y)

        if evento.type == pygame.KEYUP:
            # Soltar estación de procesamiento
            if evento.key in (self.teclas['accion1'], self.teclas['accion2']):
                if self._estacion_activa and hasattr(self._estacion_activa, 'soltar'):
                    self._estacion_activa.soltar()
                    self._estacion_activa = None

    def actualizar(self, teclas_presionadas: dict,
                   grid: list[list], filas: int, cols: int,
                   offset_x: int, offset_y: int):
        """Llamar cada frame con el estado de las teclas."""
        self._mover(teclas_presionadas, grid, filas, cols)

        # Mantener acción si sigue presionada (procesamiento continuo)
        if teclas_presionadas.get(self.teclas['accion1']):
            if self._estacion_activa and hasattr(self._estacion_activa, 'actualizar'):
                self._estacion_activa.actualizar()
        else:
            if self._estacion_activa and hasattr(self._estacion_activa, 'soltar'):
                self._estacion_activa.soltar()
                self._estacion_activa = None

        # Actualizar posición píxel
        self.px = offset_x + self.col * self.tam + self.tam // 2
        self.py = offset_y + self.fila * self.tam + self.tam // 2

    # ── Movimiento ───────────────────────────────────────────────────────────
    def _mover(self, teclas, grid, filas, cols):
        if self._move_counter > 0:
            self._move_counter -= 1
            return

        mapa_dir = [
            ('up',    self.teclas['up']),
            ('down',  self.teclas['down']),
            ('left',  self.teclas['left']),
            ('right', self.teclas['right']),
        ]
        for nombre, key in mapa_dir:
            if teclas.get(key):
                df, dc = DIRS[nombre]
                nf, nc = self.fila + df, self.col + dc
                self.direccion = nombre
                if 0 <= nf < filas and 0 <= nc < cols:
                    celda = grid[nf][nc]
                    if celda is None:   # celda libre
                        self.fila = nf
                        self.col  = nc
                        self._move_counter = self._move_delay
                break

    # ── Acción ───────────────────────────────────────────────────────────────
    def _accion(self, grid, offset_x, offset_y):
        """Interactúa con la estación adyacente en la dirección actual."""
        df, dc = DIRS[self.direccion]
        tf, tc = self.fila + df, self.col + dc
        if tf < 0 or tc < 0 or tf >= len(grid) or tc >= len(grid[0]):
            return
        estacion = grid[tf][tc]
        if estacion is None:
            return

        resultado = estacion.interactuar(self)
        if resultado:
            # Si es estación procesadora, guardar referencia
            if isinstance(estacion, (TablaCortar, EstacionCocina, Freidora)):
                self._estacion_activa = estacion
            # Si es entrega, agregar ingrediente al inventario y señalizar
            # (la Cocina manager maneja la validación)

    def agregar_inventario(self, ing: Ingrediente):
        """
        Toma lo que el chef trae en la mano (Ingrediente o Plato) y lo
        deja disponible en self.inventario para que Cocina lo compare
        contra las recetas activas.
        """
        if self.ingrediente_en_mano is not None:
            self.inventario.append(self.ingrediente_en_mano)
            self.ingrediente_en_mano = None

    def limpiar_inventario(self):
        self.inventario.clear()

    # ── Dibujo ───────────────────────────────────────────────────────────────
    def dibujar(self, surface: pygame.Surface, fuente: pygame.font.Font,
                offset_x: int, offset_y: int):
        cx = offset_x + self.col * self.tam + self.tam // 2
        cy = offset_y + self.fila * self.tam + self.tam // 2
        r  = self.tam // 2 - 4

        # Sombra
        pygame.draw.circle(surface, NEGRO, (cx + 3, cy + 3), r)
        # Cuerpo
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, self.color_borde, (cx, cy), r, 3)

        # Número de jugador
        num = fuente.render(str(self.jugador_idx + 1), True, BLANCO)
        surface.blit(num, (cx - num.get_width() // 2,
                           cy - num.get_height() // 2))

        # Ingrediente en mano (burbuja sobre la cabeza)
        if self.ingrediente_en_mano:
            ing = self.ingrediente_en_mano
            bx, by = cx - 18, cy - r - 28
            pygame.draw.rect(surface, NEGRO,
                             (bx - 2, by - 2, 38, 22), border_radius=5)
            pygame.draw.rect(surface, AMARILLO,
                             (bx - 2, by - 2, 38, 22), width=2, border_radius=5)
            color_txt = VERDE if ing.esta_listo else (ROJO if ing.esta_quemado else CREMA)
            txt = fuente.render(ing.nombre[:4], True, color_txt)
            surface.blit(txt, (bx + 1, by + 2))

        # Indicador de dirección (pequeño triángulo)
        FLECHAS = {
            'up':    [(cx, cy - r - 2), (cx - 5, cy - r + 5), (cx + 5, cy - r + 5)],
            'down':  [(cx, cy + r + 2), (cx - 5, cy + r - 5), (cx + 5, cy + r - 5)],
            'left':  [(cx - r - 2, cy), (cx - r + 5, cy - 5), (cx - r + 5, cy + 5)],
            'right': [(cx + r + 2, cy), (cx + r - 5, cy - 5), (cx + r - 5, cy + 5)],
        }
        pygame.draw.polygon(surface, self.color_borde,
                            FLECHAS[self.direccion])
        