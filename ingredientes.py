# ingredientes.py — Jerarquía de clases para ingredientes

# ── Estados posibles de un ingrediente ──────────────────────────────────────
ESTADO_CRUDO      = "crudo"
ESTADO_PREPARADO  = "preparado"
ESTADO_COCINADO   = "cocinado"
ESTADO_QUEMADO    = "quemado"


class Ingrediente:
    """
    Clase base para todos los ingredientes del juego.
    Cada ingrediente tiene un nombre, un estado y un tiempo de preparación.
    """

    # Tiempo mínimo de preparación en frames (@ 120 FPS)
    TIEMPO_PREP_BASE = 180   # 1.5 s

    def __init__(self, nombre: str):
        self.nombre: str  = nombre
        self.estado: str  = ESTADO_CRUDO
        self._ticks_prep: int = 0        # frames acumulados en estación

    # ── Consultas ────────────────────────────────────────────────────────────
    @property
    def esta_listo(self) -> bool:
        """True si el ingrediente ya fue preparado correctamente."""
        return self.estado == ESTADO_PREPARADO or self.estado == ESTADO_COCINADO

    @property
    def esta_quemado(self) -> bool:
        return self.estado == ESTADO_QUEMADO

    def progreso_prep(self) -> float:
        """Fracción 0.0–1.0 de avance en la estación actual."""
        return min(self._ticks_prep / self.TIEMPO_PREP_BASE, 1.0)

    # ── Procesamiento ────────────────────────────────────────────────────────
    def tick_preparacion(self) -> bool:
        """
        Llamar cada frame mientras el chef permanece en la estación.
        Retorna True cuando el ingrediente queda listo.
        """
        if self.estado not in (ESTADO_CRUDO,):
            return False
        self._ticks_prep += 1
        if self._ticks_prep >= self.TIEMPO_PREP_BASE:
            self._completar_preparacion()
            return True
        return False

    def _completar_preparacion(self):
        """Subclases sobreescriben para definir el estado final."""
        self.estado = ESTADO_PREPARADO

    def reiniciar(self):
        """Devuelve el ingrediente a estado crudo (para reciclaje de objetos)."""
        self.estado = ESTADO_CRUDO
        self._ticks_prep = 0

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.nombre}' [{self.estado}]>"


# ── Subclase: Vegetales y Frutas ─────────────────────────────────────────────
class VegetalFruta(Ingrediente):
    """
    Se prepara en la Tabla de Picar.
    Estado final: PREPARADO (cortado).
    """
    TIEMPO_PREP_BASE = 150   # 1.25 s — un poco más rápido

    def __init__(self, nombre: str):
        super().__init__(nombre)

    def _completar_preparacion(self):
        self.estado = ESTADO_PREPARADO   # "cortado"


# ── Subclase: Panes y Bases ──────────────────────────────────────────────────
class PanYBase(Ingrediente):
    """
    Ingrediente base (arroz, masa, alga…).
    Se obtiene directamente de la despensa; ya está listo desde el inicio.
    """
    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.estado = ESTADO_PREPARADO   # listo de fábrica

    def tick_preparacion(self) -> bool:
        # No requiere procesamiento adicional
        return True

    @property
    def esta_listo(self) -> bool:
        return True


# ── Subclase: Proteína ───────────────────────────────────────────────────────
class Proteina(Ingrediente):
    """
    Se cocina en la Estación de Cocina (sartén).
    Tiene tiempo mínimo (TIEMPO_PREP_BASE) y tiempo máximo (TIEMPO_QUEMADO)
    antes de quemarse.
    """
    TIEMPO_PREP_BASE  = 240   # 2 s mínimo para cocinar
    TIEMPO_QUEMADO    = 480   # 4 s máximo antes de quemarse

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.cocinada: bool = False

    def tick_preparacion(self) -> bool:
        if self.estado == ESTADO_QUEMADO:
            return False
        if self.estado == ESTADO_COCINADO:
            # Seguir contando para detectar quemado
            self._ticks_prep += 1
            if self._ticks_prep >= self.TIEMPO_QUEMADO:
                self.estado = ESTADO_QUEMADO
                self.cocinada = False
            return False   # ya estaba listo antes
        # Estado crudo
        self._ticks_prep += 1
        if self._ticks_prep >= self.TIEMPO_PREP_BASE:
            self._completar_preparacion()
            return True
        return False

    def _completar_preparacion(self):
        self.estado   = ESTADO_COCINADO
        self.cocinada = True

    @property
    def esta_listo(self) -> bool:
        return self.estado == ESTADO_COCINADO


# ════════════════════════════════════════════════════════════════════════════
#  CATÁLOGO DE INGREDIENTES POR ESCENARIO
# ════════════════════════════════════════════════════════════════════════════

def crear_ingrediente(nombre: str) -> Ingrediente:
    """
    Fábrica: dado el nombre de un ingrediente, retorna la instancia correcta.
    """
    PROTEINAS = {
        "Carne", "Pepperoni", "Jamón", "Salmón", "Cangrejo"
    }
    VEGETALES = {
        "Frijoles", "Ensalada", "Queso", "Aguacate", "Tofu"
    }
    BASES = {
        "Arroz", "Masa", "Salsa", "Alga"
    }

    if nombre in PROTEINAS:
        return Proteina(nombre)
    elif nombre in VEGETALES:
        return VegetalFruta(nombre)
    elif nombre in BASES:
        return PanYBase(nombre)
    else:
        raise ValueError(f"Ingrediente desconocido: '{nombre}'")


# ── Catálogos por escenario (para las despensas) ─────────────────────────────

INGREDIENTES_SODA_TICA = ["Arroz", "Frijoles", "Carne", "Ensalada"]

INGREDIENTES_PIZZERIA  = ["Masa", "Salsa", "Queso", "Pepperoni", "Jamón"]

INGREDIENTES_SUSHI     = ["Arroz", "Salmón", "Aguacate", "Cangrejo", "Alga", "Tofu"]


# ════════════════════════════════════════════════════════════════════════════
#  PLATO — combinación de varios ingredientes lista para entregar
# ════════════════════════════════════════════════════════════════════════════
class Plato:
    """
    Representa varios ingredientes combinados sobre un mostrador/mesa.
    El chef puede cargar un Plato en su mano igual que un Ingrediente
    individual, y entregarlo en la EstacionEntrega para que se compare
    contra las recetas activas.
    """

    def __init__(self):
        self.ingredientes: list[Ingrediente] = []

    def agregar(self, ing: Ingrediente) -> bool:
        """Agrega un ingrediente al plato si ya está listo para servir."""
        if ing is None or not ing.esta_listo:
            return False
        self.ingredientes.append(ing)
        return True

    @property
    def esta_vacio(self) -> bool:
        return len(self.ingredientes) == 0

    @property
    def nombre(self) -> str:
        if self.esta_vacio:
            return "Plato vacío"
        return " + ".join(i.nombre for i in self.ingredientes)

    @property
    def esta_listo(self) -> bool:
        # Un plato siempre se considera "listo" si tiene algo dentro;
        # cada ingrediente que contiene ya pasó su propia preparación.
        return not self.esta_vacio

    @property
    def esta_quemado(self) -> bool:
        return any(i.esta_quemado for i in self.ingredientes)

    @property
    def estado(self) -> str:
        return f"{len(self.ingredientes)} ing."

    def __repr__(self):
        return f"<Plato [{self.nombre}]>"
    