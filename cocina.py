# cocina.py — Manager principal de la partida

import pygame                                              # Motor del juego
import random                                               # No se usa directamente aquí, pero queda disponible
from constantes import *                                    # Colores, tamaños y estados globales
from recetas import Receta, generar_receta                  # Clase de pedido y generador aleatorio
from chef import Chef                                        # Personaje jugable
from mapas import cargar_mapa, obtener_estacion_entrega     # Carga de grilla y búsqueda de la entrega
from estaciones import EstacionEntrega                       # Tipo de estación de entrega
from ingredientes import Plato                               # Combinación de ingredientes

# Tiempo total de una partida en frames
DURACION_PARTIDA = {
    0: 120 * 120,   # Soda Tica  — 2 min     # 120 fps * 120 s
    1: 120 * 150,   # Pizzería   — 2.5 min   # 120 fps * 150 s
    2: 120 * 180,   # Sushi      — 3 min     # 120 fps * 180 s
}

# Intervalo de generación de nuevas recetas (frames)
INTERVALO_RECETA = 120 * 15   # cada 15 s   # 120 fps * 15 s

# Máximo de recetas activas al mismo tiempo
MAX_RECETAS_ACTIVAS = 4   # Tope de pedidos simultáneos en cola

# Teclas por jugador
TECLAS_J1 = {
    'up':     pygame.K_w,        # Mover arriba
    'down':   pygame.K_s,        # Mover abajo
    'left':   pygame.K_a,        # Mover izquierda
    'right':  pygame.K_d,        # Mover derecha
    'accion1': pygame.K_q,       # Acción principal (usar estación)
    'accion2': pygame.K_e,       # Acción secundaria
}
TECLAS_J2 = {
    'up':     pygame.K_i,        # Mover arriba
    'down':   pygame.K_k,        # Mover abajo
    'left':   pygame.K_j,        # Mover izquierda
    'right':  pygame.K_l,        # Mover derecha
    'accion1': pygame.K_u,       # Acción principal (usar estación)
    'accion2': pygame.K_o,       # Acción secundaria
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
        self.escenario_idx  = escenario_idx               # Índice del restaurante
        self.num_jugadores  = num_jugadores               # Cantidad de jugadores

        # Cargar mapa
        (self.grid,                                       # Matriz de estaciones
         pos1, pos2,                                       # Posiciones iniciales de chefs
         self.filas, self.cols) = cargar_mapa(escenario_idx)  # Dimensiones de la grilla

        self.tam = 60   # tamaño celda en px            # Tamaño visual de cada celda

        # Calcular offset para centrar el mapa en pantalla
        ancho_mapa = self.cols * self.tam                 # Ancho total del mapa en px
        alto_mapa  = self.filas * self.tam                # Alto total del mapa en px
        self.off_x = (ANCHO - ancho_mapa) // 2             # Margen horizontal para centrar
        self.off_y = (ALTO  - alto_mapa)  // 2 + 10        # Margen vertical para centrar (+HUD)

        # Chefs
        self.chefs: list[Chef] = [
            Chef(0, pos1[0], pos1[1], TECLAS_J1, self.tam),   # Chef 1 siempre presente
        ]
        if num_jugadores >= 2:                              # Si hay segundo jugador
            self.chefs.append(
                Chef(1, pos2[0], pos2[1], TECLAS_J2, self.tam)  # Añade Chef 2
            )

        # Estación de entrega
        self.estacion_entrega: EstacionEntrega | None = (
            obtener_estacion_entrega(self.grid)            # Busca la estación de entrega en el grid
        )

        # Recetas
        self.recetas_activas: list[Receta] = []             # Cola de pedidos en curso
        self._ticks_receta = 0                               # Contador para generar nuevas recetas
        # Generar 2 recetas iniciales
        for _ in range(2):
            self.recetas_activas.append(generar_receta(escenario_idx))  # Añade pedido inicial

        # Tiempo y puntuación
        self.tiempo_restante: int = DURACION_PARTIDA.get(escenario_idx, 120*120)  # Tiempo de partida
        self.puntuacion: int = 0                             # Puntuación acumulada
        self.terminado: bool = False                         # Bandera de fin de partida

        # Fuente local
        self.fuente_est  = pygame.font.SysFont("arial", 11)    # Fuente para texto en estaciones
        self.fuente_chef = pygame.font.SysFont("impact", 13)   # Fuente para texto en chefs

        # Mensajes flotantes de feedback
        self._mensajes: list[dict] = []                       # Lista de mensajes temporales en pantalla

    # ── Ciclo principal ──────────────────────────────────────────────────────
    def manejar_evento(self, evento: pygame.event.Event):
        for chef in self.chefs:                                            # Por cada chef
            chef.manejar_evento(evento, self.grid, self.off_x, self.off_y)  # Procesa su input

        # Detectar interacción con estación de entrega
        if evento.type == pygame.KEYDOWN:                                  # Si se presionó tecla
            for chef in self.chefs:                                        # Revisa cada chef
                key = evento.key
                if key in (chef.teclas['accion1'], chef.teclas['accion2']):  # Si fue tecla de acción
                    self._intentar_entrega(chef)                            # Intenta entregar pedido

    def actualizar(self):
        if self.terminado:                  # Si ya terminó, no hacer nada más
            return

        # Countdown
        self.tiempo_restante -= 1           # Resta un frame al tiempo restante
        if self.tiempo_restante <= 0:       # Si se acabó el tiempo
            self.tiempo_restante = 0        # Evita valores negativos
            self.terminado = True           # Marca la partida como finalizada
            return

        # Mover chefs
        teclas = pygame.key.get_pressed()                          # Estado de todas las teclas
        keys_bool = {k: teclas[k] for k in range(len(teclas))}     # Convierte a diccionario
        for chef in self.chefs:                                    # Por cada chef
            chef.actualizar(keys_bool, self.grid, self.filas, self.cols,
                            self.off_x, self.off_y)                # Actualiza movimiento/acción

        # Actualizar estaciones
        for fila in self.grid:                  # Recorre cada fila de la grilla
            for est in fila:                    # Recorre cada celda
                if est:                         # Si hay una estación
                    est.actualizar()            # Actualiza su lógica (cocción, feedback, etc.)

        # Actualizar recetas
        for receta in self.recetas_activas[:]:                    # Copia de la lista para iterar seguro
            resultado = receta.actualizar()                       # Avanza el tiempo de la receta
            if resultado == 'expirada':                            # Si la receta expiró
                self.puntuacion = max(0, self.puntuacion - receta.puntos_base)  # Penaliza puntuación
                self._agregar_mensaje(f"-{receta.puntos_base} ¡Expiró!", ROJO)  # Mensaje en pantalla
                self.recetas_activas.remove(receta)                # Elimina la receta de la cola

        # Generar nuevas recetas
        self._ticks_receta += 1                                    # Avanza contador de generación
        if (self._ticks_receta >= INTERVALO_RECETA and             # Si pasó el intervalo
                len(self.recetas_activas) < MAX_RECETAS_ACTIVAS and  # y hay espacio en la cola
                self.tiempo_restante > 0):                          # y la partida sigue activa
            self.recetas_activas.append(generar_receta(self.escenario_idx))  # Añade nueva receta
            self._ticks_receta = 0                                  # Reinicia el contador

        # Actualizar mensajes flotantes
        self._mensajes = [m for m in self._mensajes if m['ticks'] > 0]  # Elimina mensajes expirados
        for m in self._mensajes:               # Por cada mensaje activo
            m['ticks'] -= 1                    # Reduce su tiempo de vida
            m['y']     -= 0.5                  # Lo desplaza hacia arriba

    # ── Entrega ──────────────────────────────────────────────────────────────
    def _intentar_entrega(self, chef: Chef):
        """
        Verifica si el chef está frente a la estación de entrega
        y si lo que trae en la mano (ingrediente suelto o Plato)
        completa alguna receta activa.
        """
        if not self.estacion_entrega:           # Si no existe estación de entrega
            return
        ef, ec = self.estacion_entrega.fila, self.estacion_entrega.col  # Posición de la entrega

        from chef import DIRS                                      # Importa diccionario de direcciones
        df, dc = DIRS[chef.direccion]                               # Vector según orientación del chef
        if chef.fila + df != ef or chef.col + dc != ec:             # Si no está mirando la entrega
            return   # no está mirando la estación de entrega

        if chef.ingrediente_en_mano is None:        # Si no trae nada en la mano
            return   # no trae nada que entregar

        # Tomar lo que trae el chef (Ingrediente individual o Plato)
        entrega = chef.ingrediente_en_mano          # Guarda referencia a lo que entrega
        chef.ingrediente_en_mano = None             # Vacía la mano del chef

        if isinstance(entrega, Plato):                          # Si es un plato combinado
            ingredientes_a_comparar = entrega.ingredientes        # Usa su lista interna
        else:                                                     # Si es un ingrediente suelto
            ingredientes_a_comparar = [entrega]                   # Lo envuelve en una lista

        # Comparar contra recetas activas
        for receta in self.recetas_activas:                      # Revisa cada pedido activo
            if receta.comparar_receta(ingredientes_a_comparar):   # Si coincide exactamente
                # ¡Éxito!
                pts = receta.puntos_receta                        # Toma los puntos actuales
                self.puntuacion += pts                             # Suma a la puntuación total
                receta.marcar_entregada()                          # Marca la receta como completada
                self.recetas_activas.remove(receta)                # La quita de la cola
                chef.limpiar_inventario()                          # Limpia inventario del chef
                self.estacion_entrega.mostrar_feedback('ok')       # Muestra feedback visual positivo
                self._agregar_mensaje(f"+{pts} ¡Perfecto!", VERDE) # Mensaje de éxito
                return                                              # Termina la función

        # Fallo — ingrediente incorrecto o receta no coincide
        chef.limpiar_inventario()                                  # Limpia inventario igual
        self.estacion_entrega.mostrar_feedback('fail')             # Feedback visual de error
        self._agregar_mensaje("¡Incorrecto!", ROJO)                # Mensaje de fallo

    # ── Mensajes flotantes ───────────────────────────────────────────────────
    def _agregar_mensaje(self, texto: str, color: tuple):
        self._mensajes.append({
            'texto': texto,                 # Texto a mostrar
            'color': color,                 # Color del texto
            'y':     float(ALTO // 2),      # Posición vertical inicial
            'ticks': 90,                    # Duración en frames
        })

    # ── Dibujo ───────────────────────────────────────────────────────────────
    def dibujar(self, surface: pygame.Surface):
        # Fondo de suelo
        surface.fill(CAFE_OSCURO)                          # Pinta el fondo general
        for f in range(self.filas):                        # Recorre filas de la grilla
            for c in range(self.cols):                      # Recorre columnas
                rx = self.off_x + c * self.tam              # Posición x en píxeles
                ry = self.off_y + f * self.tam               # Posición y en píxeles
                color = CAFE_MEDIO if (f + c) % 2 == 0 else GRIS_OSC  # Patrón ajedrezado
                pygame.draw.rect(surface, color,
                                 (rx, ry, self.tam, self.tam))         # Dibuja celda de piso
                pygame.draw.rect(surface, NEGRO,
                                 (rx, ry, self.tam, self.tam), 1)       # Dibuja borde de celda

        # Estaciones
        for f in range(self.filas):                  # Recorre filas
            for c in range(self.cols):                # Recorre columnas
                est = self.grid[f][c]                 # Estación en esa celda
                if est:                                # Si hay una estación
                    rx = self.off_x + c * self.tam     # Posición x en píxeles
                    ry = self.off_y + f * self.tam     # Posición y en píxeles
                    rect = pygame.Rect(rx, ry, self.tam, self.tam)   # Rectángulo de la celda
                    est.dibujar(surface, rect, self.fuente_est)      # Dibuja la estación

        # Chefs
        for chef in self.chefs:                                          # Por cada chef
            chef.dibujar(surface, self.fuente_chef, self.off_x, self.off_y)  # Lo dibuja en pantalla

        # Mensajes flotantes
        fuente_msg = pygame.font.SysFont("impact", 22)        # Fuente para mensajes de feedback
        for m in self._mensajes:                              # Por cada mensaje activo
            txt = fuente_msg.render(m['texto'], True, m['color'])  # Renderiza el texto
            surface.blit(txt, (ANCHO // 2 - txt.get_width() // 2, int(m['y'])))  # Lo centra y dibuja