# recetas.py — Clase Receta y definición de recetas por escenario

import random
from ingredientes import (
    Ingrediente, crear_ingrediente,
    ESTADO_PREPARADO, ESTADO_COCINADO
)

# Puntos base por ingrediente
PUNTOS_POR_INGREDIENTE = 100    # Puntos otorgados por cada ingrediente de la receta

# Tiempo máximo de entrega en frames (@ 120 FPS) por ingrediente
TIEMPO_POR_INGREDIENTE = 120 * 20   # 20 segundos por ingrediente    # Frames de margen por ingrediente


class Receta:
    """
    Representa un pedido activo en la cola del restaurante.

    Atributos:
        nombre          — nombre del platillo
        ingredientes    — lista de Ingrediente requeridos (instancias frescas)
        puntos_receta   — puntuación actual (decrece con penalizaciones)
        puntos_base     — puntuación original (para descontar si expira)
        tiempo_max      — frames disponibles para entregar
        tiempo_restante — countdown actual
        entregada       — True si fue completada exitosamente
        expirada        — True si los puntos llegaron a 0
    """

    def __init__(self, nombre: str, lista_ingredientes: list[str]):
        self.nombre = nombre                      # Nombre del platillo
        n = len(lista_ingredientes)                 # Cantidad de ingredientes requeridos

        # Crear instancias frescas de cada ingrediente
        self.ingredientes: list[Ingrediente] = [
            crear_ingrediente(ing) for ing in lista_ingredientes   # Crea cada ingrediente requerido
        ]
        self.nombres_requeridos: list[str] = list(lista_ingredientes)   # Copia de nombres requeridos

        self.puntos_base:    int = n * PUNTOS_POR_INGREDIENTE     # Puntos totales posibles
        self.puntos_receta:  int = self.puntos_base                # Puntos actuales (decrecen)
        self.tiempo_max:     int = n * TIEMPO_POR_INGREDIENTE      # Tiempo total disponible
        self.tiempo_restante: int = self.tiempo_max                 # Countdown actual

        self.entregada: bool = False    # Si ya fue completada
        self.expirada:  bool = False    # Si se quedó sin puntos

    # ── Ciclo de vida ────────────────────────────────────────────────────────
    def actualizar(self) -> str | None:
        """
        Llamar cada frame. Maneja el countdown y penalizaciones.
        Retorna:
          'penalizada'  — se agotó el intervalo y se redujo la puntuación
          'expirada'    — puntos llegaron a 0, receta eliminada
          None          — sin cambios
        """
        if self.entregada or self.expirada:    # Si ya terminó su ciclo de vida
            return None

        self.tiempo_restante -= 1               # Resta un frame al tiempo restante

        if self.tiempo_restante <= 0:           # Si se acabó el tiempo del intervalo
            # Reducir puntos a la mitad
            self.puntos_receta //= 2             # Reduce los puntos a la mitad
            if self.puntos_receta <= 0:          # Si ya no quedan puntos
                self.puntos_receta = 0            # Evita valores negativos
                self.expirada = True              # Marca la receta como expirada
                return 'expirada'
            # Reiniciar countdown con el mismo intervalo
            self.tiempo_restante = self.tiempo_max   # Reinicia el countdown
            return 'penalizada'

        return None

    def progreso_tiempo(self) -> float:
        """Fracción 0.0–1.0 del tiempo restante (1.0 = tiempo completo)."""
        return self.tiempo_restante / self.tiempo_max    # Fracción de tiempo restante

    # ── Validación de entrega ────────────────────────────────────────────────
    def comparar_receta(self, ingredientes_entregados: list[Ingrediente]) -> bool:
        """
        Recibe la lista de ingredientes que el chef quiere entregar.
        Retorna True si coinciden exactamente con los requeridos
        (mismo nombre y estado listo/cocinado).
        """
        if len(ingredientes_entregados) != len(self.nombres_requeridos):   # Si la cantidad no coincide
            return False

        nombres_entregados = sorted(
            [ing.nombre for ing in ingredientes_entregados
             if ing.esta_listo]                                            # Solo cuenta los que están listos
        )
        nombres_requeridos = sorted(self.nombres_requeridos)               # Ordena los requeridos

        return nombres_entregados == nombres_requeridos    # Compara ambas listas ordenadas

    def marcar_entregada(self):
        self.entregada = True    # Marca la receta como completada exitosamente

    def __repr__(self):
        return (f"<Receta '{self.nombre}' "
                f"pts={self.puntos_receta} "
                f"t={self.tiempo_restante}>")    # Representación útil para depurar


# ════════════════════════════════════════════════════════════════════════════
#  PLANTILLAS DE RECETAS POR ESCENARIO
#  Formato: { "nombre": [lista de ingredientes requeridos] }
# ════════════════════════════════════════════════════════════════════════════

RECETAS_SODA_TICA = {
    "Gallo Pinto": ["Arroz", "Frijoles"],                 # Receta de gallo pinto
    "Casado":      ["Arroz", "Carne", "Ensalada"],        # Receta de casado
}

RECETAS_PIZZERIA = {
    "Margarita":  ["Masa", "Salsa", "Queso"],             # Receta de pizza margarita
    "Pepperoni":  ["Masa", "Salsa", "Pepperoni"],         # Receta de pizza de pepperoni
    "Calzone":    ["Masa", "Queso", "Jamón"],             # Receta de calzone
}

RECETAS_SUSHI = {
    "California Roll": ["Arroz", "Cangrejo", "Aguacate"],   # Receta de california roll
    "Nigiri":          ["Arroz", "Salmón"],                  # Receta de nigiri
    "Temaki":          ["Arroz", "Salmón", "Aguacate"],      # Receta de temaki
    "Miso Soup":       ["Tofu", "Alga"],                      # Receta de sopa miso
}

# Mapa escenario_idx → plantillas
RECETAS_POR_ESCENARIO = [
    RECETAS_SODA_TICA,    # Recetas del escenario 0
    RECETAS_PIZZERIA,     # Recetas del escenario 1
    RECETAS_SUSHI,        # Recetas del escenario 2
]


def generar_receta(escenario_idx: int) -> Receta:
    """
    Genera una receta aleatoria del escenario indicado.
    """
    plantillas = RECETAS_POR_ESCENARIO[escenario_idx]    # Plantillas del escenario actual
    nombre = random.choice(list(plantillas.keys()))       # Elige un nombre de receta al azar
    return Receta(nombre, plantillas[nombre])              # Crea la receta con sus ingredientes
