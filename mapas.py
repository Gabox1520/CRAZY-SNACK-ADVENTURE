# mapas.py — Diseño fijo de los 3 mapas (grilla de estaciones)

from estaciones import (Despensa, TablaCortar, EstacionCocina,
                        Freidora, Mostrador, EstacionEntrega)
from ingredientes import (INGREDIENTES_SODA_TICA,
                           INGREDIENTES_PIZZERIA, INGREDIENTES_SUSHI)

TAM_CELDA = 60

# Retorna (grid, pos_chef1, pos_chef2, filas, cols)
# grid[fila][col] = Estacion | None  (None = celda libre/suelo)


def _mapa_soda_tica():
    """
    Mapa 0 — Soda Tica  (Fácil)
    Grilla 7 filas x 11 cols
    Ingredientes: Arroz, Frijoles, Carne, Ensalada
    Recetas: Gallo Pinto (Arroz+Frijoles), Casado (Arroz+Carne+Ensalada)

    Leyenda:
      A=Arroz  F=Frijoles  Ca=Carne  En=Ensalada
      T=TablaCortar  Co=Cocina  M=Mostrador  E=Entrega  .=libre
    """
    G = 7
    C = 11
    grid = [[None]*C for _ in range(G)]

    # Fila 0 — pared norte: despensas
    grid[0][1]  = Despensa("Arroz",    0, 1)
    grid[0][3]  = Despensa("Frijoles", 0, 3)
    grid[0][5]  = Despensa("Carne",    0, 5)
    grid[0][7]  = Despensa("Ensalada", 0, 7)

    # Fila 1 — mostradores norte
    grid[1][0]  = Mostrador(1, 0)
    grid[1][10] = Mostrador(1, 10)

    # Fila 2 — isla central norte
    grid[2][2]  = TablaCortar(2, 2)
    grid[2][4]  = TablaCortar(2, 4)
    grid[2][6]  = EstacionCocina(2, 6)
    grid[2][8]  = Mostrador(2, 8)

    # Fila 4 — isla central sur
    grid[4][2]  = Mostrador(4, 2)
    grid[4][4]  = TablaCortar(4, 4)
    grid[4][6]  = EstacionCocina(4, 6)
    grid[4][8]  = Mostrador(4, 8)

    # Fila 5 — mostradores sur
    grid[5][0]  = Mostrador(5, 0)
    grid[5][10] = Mostrador(5, 10)

    # Fila 6 — pared sur: entrega
    grid[6][5]  = EstacionEntrega(6, 5)

    pos_chef1 = (3, 1)
    pos_chef2 = (3, 9)
    return grid, pos_chef1, pos_chef2, G, C


def _mapa_pizzeria():
    """
    Mapa 1 — Pizzería Roma  (Medio)
    Grilla 7 filas x 13 cols
    Ingredientes: Masa, Salsa, Queso, Pepperoni, Jamón
    Recetas: Margarita, Pepperoni, Calzone
    """
    G = 7
    C = 13
    grid = [[None]*C for _ in range(G)]

    # Fila 0 — despensas
    grid[0][1]  = Despensa("Masa",      0, 1)
    grid[0][3]  = Despensa("Salsa",     0, 3)
    grid[0][5]  = Despensa("Queso",     0, 5)
    grid[0][7]  = Despensa("Pepperoni", 0, 7)
    grid[0][9]  = Despensa("Jamón",     0, 9)

    # Bordes
    grid[1][0]  = Mostrador(1, 0)
    grid[1][12] = Mostrador(1, 12)

    # Isla norte
    grid[2][2]  = TablaCortar(2, 2)
    grid[2][4]  = TablaCortar(2, 4)
    grid[2][6]  = EstacionCocina(2, 6)
    grid[2][8]  = EstacionCocina(2, 8)
    grid[2][10] = Mostrador(2, 10)

    # Isla sur
    grid[4][2]  = Mostrador(4, 2)
    grid[4][4]  = TablaCortar(4, 4)
    grid[4][6]  = EstacionCocina(4, 6)
    grid[4][8]  = Mostrador(4, 8)
    grid[4][10] = Mostrador(4, 10)

    # Bordes
    grid[5][0]  = Mostrador(5, 0)
    grid[5][12] = Mostrador(5, 12)

    # Entrega
    grid[6][6]  = EstacionEntrega(6, 6)

    pos_chef1 = (3, 1)
    pos_chef2 = (3, 11)
    return grid, pos_chef1, pos_chef2, G, C


def _mapa_sushi():
    """
    Mapa 2 — Sushi Bar Kyoto  (Difícil)
    Grilla 8 filas x 13 cols
    Ingredientes: Arroz, Salmon, Aguacate, Cangrejo, Alga, Tofu
    Recetas: California Roll, Nigiri, Temaki, Miso Soup
    """
    G = 8
    C = 13
    grid = [[None]*C for _ in range(G)]

    # Despensas — fila 0
    grid[0][1]  = Despensa("Arroz",    0, 1)
    grid[0][3]  = Despensa("Salmón",   0, 3)
    grid[0][5]  = Despensa("Aguacate", 0, 5)
    grid[0][7]  = Despensa("Cangrejo", 0, 7)
    grid[0][9]  = Despensa("Alga",     0, 9)
    grid[0][11] = Despensa("Tofu",     0, 11)

    # Pared oeste/este
    grid[1][0]  = Mostrador(1, 0)
    grid[1][12] = Mostrador(1, 12)
    grid[6][0]  = Mostrador(6, 0)
    grid[6][12] = Mostrador(6, 12)

    # Isla norte
    grid[2][2]  = TablaCortar(2, 2)
    grid[2][4]  = TablaCortar(2, 4)
    grid[2][6]  = EstacionCocina(2, 6)
    grid[2][8]  = EstacionCocina(2, 8)
    grid[2][10] = Mostrador(2, 10)

    # Isla central
    grid[4][3]  = Mostrador(4, 3)
    grid[4][5]  = TablaCortar(4, 5)
    grid[4][7]  = EstacionCocina(4, 7)
    grid[4][9]  = Mostrador(4, 9)

    # Isla sur
    grid[6][2]  = Mostrador(6, 2)
    grid[6][4]  = TablaCortar(6, 4)
    grid[6][6]  = Mostrador(6, 6)
    grid[6][8]  = Mostrador(6, 8)
    grid[6][10] = Mostrador(6, 10)

    # Entrega
    grid[7][6]  = EstacionEntrega(7, 6)

    pos_chef1 = (3, 1)
    pos_chef2 = (5, 11)
    return grid, pos_chef1, pos_chef2, G, C


MAPAS = [_mapa_soda_tica, _mapa_pizzeria, _mapa_sushi]


def cargar_mapa(escenario_idx: int):
    """Retorna (grid, pos_chef1, pos_chef2, filas, cols)."""
    return MAPAS[escenario_idx]()


def obtener_estacion_entrega(grid):
    """Busca y retorna la EstacionEntrega del grid."""
    for fila in grid:
        for celda in fila:
            if isinstance(celda, EstacionEntrega):
                return celda
    return None
