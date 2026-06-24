# chef.py — Clase Chef con movimiento en grilla e interacción con estaciones

import pygame                                                   # Motor del juego
from constantes import *                                        # Colores y constantes globales
from ingredientes import Ingrediente                             # Tipo de objeto que el chef puede llevar
from estaciones import (Estacion, TablaCortar, EstacionCocina,
                        Freidora, Mostrador, EstacionEntrega, Despensa)  # Tipos de estaciones

TAM_CELDA = 60   # píxeles por celda (debe coincidir con el mapa)   # Tamaño visual de cada celda

# Dirección → (dfila, dcol)
DIRS = {
    'up':    (-1,  0),     # Arriba: resta una fila
    'down':  ( 1,  0),     # Abajo: suma una fila
    'left':  ( 0, -1),     # Izquierda: resta una columna
    'right': ( 0,  1),     # Derecha: suma una columna
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
        (255, 160, 80),   # Borde Chef 1
        (100, 180, 255),  # Borde Chef 2
    ]

    def __init__(self, jugador_idx: int, fila: int, col: int,
                 teclas: dict, tam_celda: int = TAM_CELDA):
        self.jugador_idx = jugador_idx        # 0 = jugador 1, 1 = jugador 2
        self.fila = fila                      # Fila actual en la grilla
        self.col  = col                       # Columna actual en la grilla
        self.tam  = tam_celda                 # Tamaño de celda en píxeles

        # Teclas: {'up', 'down', 'left', 'right', 'accion1', 'accion2'}
        self.teclas = teclas                  # Mapeo de teclas asignadas a este chef

        self.ingrediente_en_mano: Ingrediente | None = None   # Lo que el chef sostiene
        self.direccion = 'down'                                # Hacia dónde mira el chef

        # Movimiento con delay para no moverse 120 veces por segundo
        self._move_delay   = 8    # frames entre pasos       # Espera entre movimientos
        self._move_counter = 0                                 # Contador hacia el siguiente paso

        # Referencia a la estación activa (procesando)
        self._estacion_activa: Estacion | None = None         # Estación que se está usando

        # Inventario acumulado para entrega (lista de hasta 3 ings)
        self.inventario: list[Ingrediente] = []                # Ingredientes acumulados

        # Offset de dibujo (posición en píxeles, para smooth visual)
        self.px = 0       # Posición x en píxeles
        self.py = 0       # Posición y en píxeles

        self.color       = self.COLORES[jugador_idx]        # Color del cuerpo según jugador
        self.color_borde = self.COLORES_BORDE[jugador_idx]  # Color del borde según jugador

    # ── Input ────────────────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event,
                       grid: list[list], offset_x: int, offset_y: int):
        """
        Procesa eventos de teclado del jugador.
        grid: matriz 2D de Estacion|None
        """
        if evento.type == pygame.KEYDOWN:                       # Si se presionó una tecla
            # Acción principal — recoger/usar estación
            if evento.key == self.teclas['accion1']:            # Si es la tecla de acción 1
                self._accion(grid, offset_x, offset_y)          # Ejecuta la interacción

        if evento.type == pygame.KEYUP:                                          # Si se soltó una tecla
            # Soltar estación de procesamiento
            if evento.key in (self.teclas['accion1'], self.teclas['accion2']):    # Si era de acción
                if self._estacion_activa and hasattr(self._estacion_activa, 'soltar'):  # Si procesaba algo
                    self._estacion_activa.soltar()                               # Detiene el procesamiento
                    self._estacion_activa = None                                 # Limpia la referencia

    def actualizar(self, teclas_presionadas: dict,
                   grid: list[list], filas: int, cols: int,
                   offset_x: int, offset_y: int):
        """Llamar cada frame con el estado de las teclas."""
        self._mover(teclas_presionadas, grid, filas, cols)     # Intenta mover según teclas

        # Mantener acción si sigue presionada (procesamiento continuo)
        if teclas_presionadas.get(self.teclas['accion1']):                       # Si sigue presionada
            if self._estacion_activa and hasattr(self._estacion_activa, 'actualizar'):  # Y hay estación activa
                self._estacion_activa.actualizar()                               # Avanza su procesamiento
        else:                                                                     # Si ya no se presiona
            if self._estacion_activa and hasattr(self._estacion_activa, 'soltar'):  # Si había una activa
                self._estacion_activa.soltar()                                   # La detiene
                self._estacion_activa = None                                     # Limpia referencia

        # Actualizar posición píxel
        self.px = offset_x + self.col * self.tam + self.tam // 2   # Posición x centrada en celda
        self.py = offset_y + self.fila * self.tam + self.tam // 2  # Posición y centrada en celda

    # ── Movimiento ───────────────────────────────────────────────────────────
    def _mover(self, teclas, grid, filas, cols):
        if self._move_counter > 0:           # Si aún está en cooldown de movimiento
            self._move_counter -= 1          # Reduce el contador
            return                           # No se mueve este frame

        mapa_dir = [
            ('up',    self.teclas['up']),       # Tecla de subir
            ('down',  self.teclas['down']),     # Tecla de bajar
            ('left',  self.teclas['left']),     # Tecla de izquierda
            ('right', self.teclas['right']),    # Tecla de derecha
        ]
        for nombre, key in mapa_dir:                          # Revisa cada dirección posible
            if teclas.get(key):                               # Si esa tecla está presionada
                df, dc = DIRS[nombre]                          # Vector de desplazamiento
                nf, nc = self.fila + df, self.col + dc         # Nueva posición candidata
                self.direccion = nombre                        # Actualiza hacia dónde mira
                if 0 <= nf < filas and 0 <= nc < cols:         # Si está dentro del mapa
                    celda = grid[nf][nc]                       # Contenido de la celda destino
                    if celda is None:   # celda libre
                        self.fila = nf                          # Confirma el movimiento en fila
                        self.col  = nc                          # Confirma el movimiento en columna
                        self._move_counter = self._move_delay   # Reinicia el cooldown
                break                                           # Solo procesa una dirección por frame

    # ── Acción ───────────────────────────────────────────────────────────────
    def _accion(self, grid, offset_x, offset_y):
        """Interactúa con la estación adyacente en la dirección actual."""
        df, dc = DIRS[self.direccion]                           # Vector según orientación actual
        tf, tc = self.fila + df, self.col + dc                  # Celda objetivo frente al chef
        if tf < 0 or tc < 0 or tf >= len(grid) or tc >= len(grid[0]):  # Si está fuera del mapa
            return
        estacion = grid[tf][tc]                                 # Estación en la celda objetivo
        if estacion is None:                                    # Si no hay estación ahí
            return

        resultado = estacion.interactuar(self)                  # Intenta interactuar con la estación
        if resultado:                                           # Si la interacción tuvo efecto
            # Si es estación procesadora, guardar referencia
            if isinstance(estacion, (TablaCortar, EstacionCocina, Freidora)):  # Si requiere mantener tecla
                self._estacion_activa = estacion                # Guarda referencia para seguir procesando
            # Si es entrega, agregar ingrediente al inventario y señalizar
            # (la Cocina manager maneja la validación)

    def agregar_inventario(self, ing: Ingrediente):
        """
        Toma lo que el chef trae en la mano (Ingrediente o Plato) y lo
        deja disponible en self.inventario para que Cocina lo compare
        contra las recetas activas.
        """
        if self.ingrediente_en_mano is not None:        # Si el chef trae algo
            self.inventario.append(self.ingrediente_en_mano)  # Lo agrega al inventario
            self.ingrediente_en_mano = None              # Vacía la mano

    def limpiar_inventario(self):
        self.inventario.clear()                          # Vacía la lista de inventario

    # ── Dibujo ───────────────────────────────────────────────────────────────
    def dibujar(self, surface: pygame.Surface, fuente: pygame.font.Font,
                offset_x: int, offset_y: int):
        cx = offset_x + self.col * self.tam + self.tam // 2   # Centro x del chef en píxeles
        cy = offset_y + self.fila * self.tam + self.tam // 2  # Centro y del chef en píxeles
        r  = self.tam // 2 - 4                                  # Radio del círculo del chef

        # Sombra
        pygame.draw.circle(surface, NEGRO, (cx + 3, cy + 3), r)   # Sombra desplazada
        # Cuerpo
        pygame.draw.circle(surface, self.color, (cx, cy), r)               # Círculo principal
        pygame.draw.circle(surface, self.color_borde, (cx, cy), r, 3)      # Borde del círculo

        # Número de jugador
        num = fuente.render(str(self.jugador_idx + 1), True, BLANCO)       # Texto "1" o "2"
        surface.blit(num, (cx - num.get_width() // 2,                     # Centrado horizontal
                           cy - num.get_height() // 2))                   # Centrado vertical

        # Ingrediente en mano (burbuja sobre la cabeza)
        if self.ingrediente_en_mano:                                       # Si trae algo
            ing = self.ingrediente_en_mano                                 # Referencia al ingrediente
            bx, by = cx - 18, cy - r - 28                                  # Posición de la burbuja
            pygame.draw.rect(surface, NEGRO,
                             (bx - 2, by - 2, 38, 22), border_radius=5)     # Fondo de la burbuja
            pygame.draw.rect(surface, AMARILLO,
                             (bx - 2, by - 2, 38, 22), width=2, border_radius=5)  # Borde de la burbuja
            color_txt = VERDE if ing.esta_listo else (ROJO if ing.esta_quemado else CREMA)  # Color según estado
            txt = fuente.render(ing.nombre[:4], True, color_txt)           # Nombre truncado del ingrediente
            surface.blit(txt, (bx + 1, by + 2))                            # Dibuja el texto en la burbuja

        # Indicador de dirección (pequeño triángulo)
        FLECHAS = {
            'up':    [(cx, cy - r - 2), (cx - 5, cy - r + 5), (cx + 5, cy - r + 5)],    # Triángulo arriba
            'down':  [(cx, cy + r + 2), (cx - 5, cy + r - 5), (cx + 5, cy + r - 5)],    # Triángulo abajo
            'left':  [(cx - r - 2, cy), (cx - r + 5, cy - 5), (cx - r + 5, cy + 5)],    # Triángulo izquierda
            'right': [(cx + r + 2, cy), (cx + r - 5, cy - 5), (cx + r - 5, cy + 5)],    # Triángulo derecha
        }
        pygame.draw.polygon(surface, self.color_borde,
                            FLECHAS[self.direccion])                        # Dibuja la flecha de dirección
        