# recetas.py — Clase Receta y definición de recetas por escenario

import random
from ingredientes import (
    Ingrediente, crear_ingrediente,
    ESTADO_PREPARADO, ESTADO_COCINADO
)

# Puntos base por ingrediente
PUNTOS_POR_INGREDIENTE = 100

# Tiempo máximo de entrega en frames (@ 120 FPS) por ingrediente
TIEMPO_POR_INGREDIENTE = 120 * 20   # 20 segundos por ingrediente


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
        self.nombre = nombre
        n = len(lista_ingredientes)

        # Crear instancias frescas de cada ingrediente
        self.ingredientes: list[Ingrediente] = [
            crear_ingrediente(ing) for ing in lista_ingredientes
        ]
        self.nombres_requeridos: list[str] = list(lista_ingredientes)

        self.puntos_base:    int = n * PUNTOS_POR_INGREDIENTE
        self.puntos_receta:  int = self.puntos_base
        self.tiempo_max:     int = n * TIEMPO_POR_INGREDIENTE
        self.tiempo_restante: int = self.tiempo_max

        self.entregada: bool = False
        self.expirada:  bool = False

    # ── Ciclo de vida ────────────────────────────────────────────────────────
    def actualizar(self) -> str | None:
        """
        Llamar cada frame. Maneja el countdown y penalizaciones.
        Retorna:
          'penalizada'  — se agotó el intervalo y se redujo la puntuación
          'expirada'    — puntos llegaron a 0, receta eliminada
          None          — sin cambios
        """
        if self.entregada or self.expirada:
            return None

        self.tiempo_restante -= 1

        if self.tiempo_restante <= 0:
            # Reducir puntos a la mitad
            self.puntos_receta //= 2
            if self.puntos_receta <= 0:
                self.puntos_receta = 0
                self.expirada = True
                return 'expirada'
            # Reiniciar countdown con el mismo intervalo
            self.tiempo_restante = self.tiempo_max
            return 'penalizada'

        return None

    def progreso_tiempo(self) -> float:
        """Fracción 0.0–1.0 del tiempo restante (1.0 = tiempo completo)."""
        return self.tiempo_restante / self.tiempo_max

    # ── Validación de entrega ────────────────────────────────────────────────
    def comparar_receta(self, ingredientes_entregados: list[Ingrediente]) -> bool:
        """
        Recibe la lista de ingredientes que el chef quiere entregar.
        Retorna True si coinciden exactamente con los requeridos
        (mismo nombre y estado listo/cocinado).
        """
        if len(ingredientes_entregados) != len(self.nombres_requeridos):
            return False

        nombres_entregados = sorted(
            [ing.nombre for ing in ingredientes_entregados
             if ing.esta_listo]
        )
        nombres_requeridos = sorted(self.nombres_requeridos)

        return nombres_entregados == nombres_requeridos

    def marcar_entregada(self):
        self.entregada = True

    def __repr__(self):
        return (f"<Receta '{self.nombre}' "
                f"pts={self.puntos_receta} "
                f"t={self.tiempo_restante}>")


# ════════════════════════════════════════════════════════════════════════════
#  PLANTILLAS DE RECETAS POR ESCENARIO
#  Formato: { "nombre": [lista de ingredientes requeridos] }
# ════════════════════════════════════════════════════════════════════════════

RECETAS_SODA_TICA = {
    "Gallo Pinto": ["Arroz", "Frijoles"],
    "Casado":      ["Arroz", "Carne", "Ensalada"],
}

RECETAS_PIZZERIA = {
    "Margarita":  ["Masa", "Salsa", "Queso"],
    "Pepperoni":  ["Masa", "Salsa", "Pepperoni"],
    "Calzone":    ["Masa", "Queso", "Jamón"],
}

RECETAS_SUSHI = {
    "California Roll": ["Arroz", "Cangrejo", "Aguacate"],
    "Nigiri":          ["Arroz", "Salmón"],
    "Temaki":          ["Arroz", "Salmón", "Aguacate"],
    "Miso Soup":       ["Tofu", "Alga"],
}

# Mapa escenario_idx → plantillas
RECETAS_POR_ESCENARIO = [
    RECETAS_SODA_TICA,
    RECETAS_PIZZERIA,
    RECETAS_SUSHI,
]


def generar_receta(escenario_idx: int) -> Receta:
    """
    Genera una receta aleatoria del escenario indicado.
    """
    plantillas = RECETAS_POR_ESCENARIO[escenario_idx]
    nombre = random.choice(list(plantillas.keys()))
    return Receta(nombre, plantillas[nombre])
