# ingredientes.py — Jerarquía de clases para ingredientes

# ── Estados posibles de un ingrediente ──────────────────────────────────────
ESTADO_CRUDO      = "crudo"          # Aún no procesado
ESTADO_PREPARADO  = "preparado"      # Cortado o listo de fábrica
ESTADO_COCINADO   = "cocinado"       # Cocinado correctamente
ESTADO_QUEMADO    = "quemado"        # Se dejó demasiado tiempo


class Ingrediente:
    """
    Clase base para todos los ingredientes del juego.
    Cada ingrediente tiene un nombre, un estado y un tiempo de preparación.
    """

    # Tiempo mínimo de preparación en frames (@ 120 FPS)
    TIEMPO_PREP_BASE = 180   # 1.5 s          # Frames necesarios para preparar

    def __init__(self, nombre: str):
        self.nombre: str  = nombre              # Nombre del ingrediente
        self.estado: str  = ESTADO_CRUDO        # Estado inicial: crudo
        self._ticks_prep: int = 0               # frames acumulados en estación   # Contador de avance

    # ── Consultas ────────────────────────────────────────────────────────────
    @property
    def esta_listo(self) -> bool:
        """True si el ingrediente ya fue preparado correctamente."""
        return self.estado == ESTADO_PREPARADO or self.estado == ESTADO_COCINADO   # Preparado o cocinado

    @property
    def esta_quemado(self) -> bool:
        return self.estado == ESTADO_QUEMADO    # True si se quemó

    def progreso_prep(self) -> float:
        """Fracción 0.0–1.0 de avance en la estación actual."""
        return min(self._ticks_prep / self.TIEMPO_PREP_BASE, 1.0)    # Limita a 1.0 como máximo

    # ── Procesamiento ────────────────────────────────────────────────────────
    def tick_preparacion(self) -> bool:
        """
        Llamar cada frame mientras el chef permanece en la estación.
        Retorna True cuando el ingrediente queda listo.
        """
        if self.estado not in (ESTADO_CRUDO,):     # Solo se procesa si está crudo
            return False
        self._ticks_prep += 1                       # Avanza un frame
        if self._ticks_prep >= self.TIEMPO_PREP_BASE:   # Si alcanzó el tiempo necesario
            self._completar_preparacion()             # Marca como completado
            return True
        return False

    def _completar_preparacion(self):
        """Subclases sobreescriben para definir el estado final."""
        self.estado = ESTADO_PREPARADO    # Estado por defecto al terminar

    def reiniciar(self):
        """Devuelve el ingrediente a estado crudo (para reciclaje de objetos)."""
        self.estado = ESTADO_CRUDO        # Vuelve a crudo
        self._ticks_prep = 0              # Reinicia el contador

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.nombre}' [{self.estado}]>"   # Representación útil para depurar


# ── Subclase: Vegetales y Frutas ─────────────────────────────────────────────
class VegetalFruta(Ingrediente):
    """
    Se prepara en la Tabla de Picar.
    Estado final: PREPARADO (cortado).
    """
    TIEMPO_PREP_BASE = 150   # 1.25 s — un poco más rápido      # Tiempo de corte específico

    def __init__(self, nombre: str):
        super().__init__(nombre)    # Inicializa con la clase base

    def _completar_preparacion(self):
        self.estado = ESTADO_PREPARADO   # "cortado"    # Al terminar queda preparado


# ── Subclase: Panes y Bases ──────────────────────────────────────────────────
class PanYBase(Ingrediente):
    """
    Ingrediente base (arroz, masa, alga…).
    Se obtiene directamente de la despensa; ya está listo desde el inicio.
    """
    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.estado = ESTADO_PREPARADO   # listo de fábrica    # No requiere preparación

    def tick_preparacion(self) -> bool:
        # No requiere procesamiento adicional
        return True    # Siempre se considera completado

    @property
    def esta_listo(self) -> bool:
        return True    # Siempre está listo


# ── Subclase: Proteína ───────────────────────────────────────────────────────
class Proteina(Ingrediente):
    """
    Se cocina en la Estación de Cocina (sartén).
    Tiene tiempo mínimo (TIEMPO_PREP_BASE) y tiempo máximo (TIEMPO_QUEMADO)
    antes de quemarse.
    """
    TIEMPO_PREP_BASE  = 240   # 2 s mínimo para cocinar         # Frames mínimos de cocción
    TIEMPO_QUEMADO    = 480   # 4 s máximo antes de quemarse    # Frames antes de quemarse

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.cocinada: bool = False    # Bandera de cocción exitosa

    def tick_preparacion(self) -> bool:
        if self.estado == ESTADO_QUEMADO:    # Si ya está quemada
            return False
        if self.estado == ESTADO_COCINADO:    # Si ya está cocinada
            # Seguir contando para detectar quemado
            self._ticks_prep += 1                          # Sigue acumulando tiempo
            if self._ticks_prep >= self.TIEMPO_QUEMADO:    # Si supera el límite
                self.estado = ESTADO_QUEMADO                # Se quema
                self.cocinada = False                        # Ya no cuenta como cocinada
            return False   # ya estaba listo antes
        # Estado crudo
        self._ticks_prep += 1                       # Avanza un frame de cocción
        if self._ticks_prep >= self.TIEMPO_PREP_BASE:   # Si alcanzó el mínimo
            self._completar_preparacion()             # Marca como cocinada
            return True
        return False

    def _completar_preparacion(self):
        self.estado   = ESTADO_COCINADO    # Cambia a cocinado
        self.cocinada = True                # Marca como cocinada exitosamente

    @property
    def esta_listo(self) -> bool:
        return self.estado == ESTADO_COCINADO   # Solo lista si está cocinada


# ════════════════════════════════════════════════════════════════════════════
#  CATÁLOGO DE INGREDIENTES POR ESCENARIO
# ════════════════════════════════════════════════════════════════════════════

def crear_ingrediente(nombre: str) -> Ingrediente:
    """
    Fábrica: dado el nombre de un ingrediente, retorna la instancia correcta.
    """
    PROTEINAS = {
        "Carne", "Pepperoni", "Jamón", "Salmón", "Cangrejo"    # Ingredientes que se cocinan
    }
    VEGETALES = {
        "Frijoles", "Ensalada", "Queso", "Aguacate", "Tofu"    # Ingredientes que se cortan
    }
    BASES = {
        "Arroz", "Masa", "Salsa", "Alga"                       # Ingredientes ya listos
    }

    if nombre in PROTEINAS:
        return Proteina(nombre)               # Crea instancia de Proteina
    elif nombre in VEGETALES:
        return VegetalFruta(nombre)           # Crea instancia de VegetalFruta
    elif nombre in BASES:
        return PanYBase(nombre)               # Crea instancia de PanYBase
    else:
        raise ValueError(f"Ingrediente desconocido: '{nombre}'")   # Error si no existe


# ── Catálogos por escenario (para las despensas) ─────────────────────────────

INGREDIENTES_SODA_TICA = ["Arroz", "Frijoles", "Carne", "Ensalada"]      # Ingredientes de la Soda Tica

INGREDIENTES_PIZZERIA  = ["Masa", "Salsa", "Queso", "Pepperoni", "Jamón"]  # Ingredientes de la Pizzería

INGREDIENTES_SUSHI     = ["Arroz", "Salmón", "Aguacate", "Cangrejo", "Alga", "Tofu"]  # Ingredientes del Sushi


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
        self.ingredientes: list[Ingrediente] = []    # Lista de ingredientes combinados

    def agregar(self, ing: Ingrediente) -> bool:
        """Agrega un ingrediente al plato si ya está listo para servir."""
        if ing is None or not ing.esta_listo:    # Si no hay ingrediente o no está listo
            return False
        self.ingredientes.append(ing)             # Lo agrega a la lista
        return True

    @property
    def esta_vacio(self) -> bool:
        return len(self.ingredientes) == 0    # True si no tiene ningún ingrediente

    @property
    def nombre(self) -> str:
        if self.esta_vacio:
            return "Plato vacío"               # Nombre por defecto si está vacío
        return " + ".join(i.nombre for i in self.ingredientes)   # Junta nombres con "+"

    @property
    def esta_listo(self) -> bool:
        # Un plato siempre se considera "listo" si tiene algo dentro;
        # cada ingrediente que contiene ya pasó su propia preparación.
        return not self.esta_vacio    # Listo si tiene al menos un ingrediente

    @property
    def esta_quemado(self) -> bool:
        return any(i.esta_quemado for i in self.ingredientes)   # True si alguno se quemó

    @property
    def estado(self) -> str:
        return f"{len(self.ingredientes)} ing."   # Texto descriptivo de cantidad

    def __repr__(self):
        return f"<Plato [{self.nombre}]>"     # Representación útil para depurar
    