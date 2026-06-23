# cocina.py — Manager principal de la partida

import pygame
import random
from constantes import *
from recetas import Receta, generar_receta
from chef import Chef
from mapas import cargar_mapa, obtener_estacion_entrega
from estaciones import EstacionEntrega
from ingredientes import Plato

# Tiempo total de una partida en frames
DURACION_PARTIDA = {
    0: 120 * 120,   # Soda Tica  — 2 min
    1: 120 * 150,   # Pizzería   — 2.5 min
    2: 120 * 180,   # Sushi      — 3 min
}

# Intervalo de generación de nuevas recetas (frames)
INTERVALO_RECETA = 120 * 15   # cada 15 s

# Máximo de recetas activas al mismo tiempo
MAX_RECETAS_ACTIVAS = 4

# Teclas por jugador
TECLAS_J1 = {
    'up':     pygame.K_w,
    'down':   pygame.K_s,
    'left':   pygame.K_a,
    'right':  pygame.K_d,
    'accion1': pygame.K_q,
    'accion2': pygame.K_e,
}
TECLAS_J2 = {
    'up':     pygame.K_i,
    'down':   pygame.K_k,
    'left':   pygame.K_j,
    'right':  pygame.K_l,
    'accion1': pygame.K_u,
    'accion2': pygame.K_o,
}


class Cocina:
    """
    Manager de la partida. Contiene y coordina:
    - Los chefs
    - Las estaciones (a través del grid del mapa)
    - Las recetas activas
    - El temporizador y la puntuación
    """

    def __init__(self, escenario_idx: int, num_jugadores: int = 1):
        self.escenario_idx  = escenario_idx
        self.num_jugadores  = num_jugadores

        # Cargar mapa
        (self.grid,
         pos1, pos2,
         self.filas, self.cols) = cargar_mapa(escenario_idx)

        self.tam = 60   # tamaño celda en px

        # Calcular offset para centrar el mapa en pantalla
        ancho_mapa = self.cols * self.tam
        alto_mapa  = self.filas * self.tam
        self.off_x = (ANCHO - ancho_mapa) // 2
        self.off_y = (ALTO  - alto_mapa)  // 2 + 10

        # Chefs
        self.chefs: list[Chef] = [
            Chef(0, pos1[0], pos1[1], TECLAS_J1, self.tam),
        ]
        if num_jugadores >= 2:
            self.chefs.append(
                Chef(1, pos2[0], pos2[1], TECLAS_J2, self.tam)
            )

        # Estación de entrega
        self.estacion_entrega: EstacionEntrega | None = (
            obtener_estacion_entrega(self.grid)
        )

        # Recetas
        self.recetas_activas: list[Receta] = []
        self._ticks_receta = 0
        # Generar 2 recetas iniciales
        for _ in range(2):
            self.recetas_activas.append(generar_receta(escenario_idx))

        # Tiempo y puntuación
        self.tiempo_restante: int = DURACION_PARTIDA.get(escenario_idx, 120*120)
        self.puntuacion: int = 0
        self.terminado: bool = False

        # Fuente local
        self.fuente_est  = pygame.font.SysFont("arial", 11)
        self.fuente_chef = pygame.font.SysFont("impact", 13)

        # Mensajes flotantes de feedback
        self._mensajes: list[dict] = []

    # ── Ciclo principal ──────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        for chef in self.chefs:
            chef.manejar_evento(evento, self.grid, self.off_x, self.off_y)

        # Detectar interacción con estación de entrega
        if evento.type == pygame.KEYDOWN:
            for chef in self.chefs:
                key = evento.key
                if key in (chef.teclas['accion1'], chef.teclas['accion2']):
                    self._intentar_entrega(chef)

    def actualizar(self):
        if self.terminado:
            return

        # Countdown
        self.tiempo_restante -= 1
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            self.terminado = True
            return

        # Mover chefs
        teclas = pygame.key.get_pressed()
        keys_bool = {k: teclas[k] for k in range(len(teclas))}
        for chef in self.chefs:
            chef.actualizar(keys_bool, self.grid, self.filas, self.cols,
                            self.off_x, self.off_y)

        # Actualizar estaciones
        for fila in self.grid:
            for est in fila:
                if est:
                    est.actualizar()

        # Actualizar recetas
        for receta in self.recetas_activas[:]:
            resultado = receta.actualizar()
            if resultado == 'expirada':
                self.puntuacion = max(0, self.puntuacion - receta.puntos_base)
                self._agregar_mensaje(f"-{receta.puntos_base} ¡Expiró!", ROJO)
                self.recetas_activas.remove(receta)

        # Generar nuevas recetas
        self._ticks_receta += 1
        if (self._ticks_receta >= INTERVALO_RECETA and
                len(self.recetas_activas) < MAX_RECETAS_ACTIVAS and
                self.tiempo_restante > 0):
            self.recetas_activas.append(generar_receta(self.escenario_idx))
            self._ticks_receta = 0

        # Actualizar mensajes flotantes
        self._mensajes = [m for m in self._mensajes if m['ticks'] > 0]
        for m in self._mensajes:
            m['ticks'] -= 1
            m['y']     -= 0.5

    # ── Entrega ──────────────────────────────────────────────────────────────
    def _intentar_entrega(self, chef: Chef):
        """
        Verifica si el chef está frente a la estación de entrega
        y si lo que trae en la mano (ingrediente suelto o Plato)
        completa alguna receta activa.
        """
        if not self.estacion_entrega:
            return
        ef, ec = self.estacion_entrega.fila, self.estacion_entrega.col

        from chef import DIRS
        df, dc = DIRS[chef.direccion]
        if chef.fila + df != ef or chef.col + dc != ec:
            return   # no está mirando la estación de entrega

        if chef.ingrediente_en_mano is None:
            return   # no trae nada que entregar

        # Tomar lo que trae el chef (Ingrediente individual o Plato)
        entrega = chef.ingrediente_en_mano
        chef.ingrediente_en_mano = None

        if isinstance(entrega, Plato):
            ingredientes_a_comparar = entrega.ingredientes
        else:
            ingredientes_a_comparar = [entrega]

        # Comparar contra recetas activas
        for receta in self.recetas_activas:
            if receta.comparar_receta(ingredientes_a_comparar):
                # ¡Éxito!
                pts = receta.puntos_receta
                self.puntuacion += pts
                receta.marcar_entregada()
                self.recetas_activas.remove(receta)
                chef.limpiar_inventario()
                self.estacion_entrega.mostrar_feedback('ok')
                self._agregar_mensaje(f"+{pts} ¡Perfecto!", VERDE)
                return

        # Fallo — ingrediente incorrecto o receta no coincide
        chef.limpiar_inventario()
        self.estacion_entrega.mostrar_feedback('fail')
        self._agregar_mensaje("¡Incorrecto!", ROJO)

    # ── Mensajes flotantes ───────────────────────────────────────────────────
    def _agregar_mensaje(self, texto: str, color: tuple):
        self._mensajes.append({
            'texto': texto,
            'color': color,
            'y':     float(ALTO // 2),
            'ticks': 90,
        })

    # ── Dibujo ───────────────────────────────────────────────────────────────
    def dibujar(self, surface: pygame.Surface):
        # Fondo de suelo
        surface.fill(CAFE_OSCURO)
        for f in range(self.filas):
            for c in range(self.cols):
                rx = self.off_x + c * self.tam
                ry = self.off_y + f * self.tam
                color = CAFE_MEDIO if (f + c) % 2 == 0 else GRIS_OSC
                pygame.draw.rect(surface, color,
                                 (rx, ry, self.tam, self.tam))
                pygame.draw.rect(surface, NEGRO,
                                 (rx, ry, self.tam, self.tam), 1)

        # Estaciones
        for f in range(self.filas):
            for c in range(self.cols):
                est = self.grid[f][c]
                if est:
                    rx = self.off_x + c * self.tam
                    ry = self.off_y + f * self.tam
                    rect = pygame.Rect(rx, ry, self.tam, self.tam)
                    est.dibujar(surface, rect, self.fuente_est)

        # Chefs
        for chef in self.chefs:
            chef.dibujar(surface, self.fuente_chef, self.off_x, self.off_y)

        # Mensajes flotantes
        fuente_msg = pygame.font.SysFont("impact", 22)
        for m in self._mensajes:
            txt = fuente_msg.render(m['texto'], True, m['color'])
            surface.blit(txt, (ANCHO // 2 - txt.get_width() // 2, int(m['y'])))
            