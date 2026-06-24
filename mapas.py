# mapas.py — Diseño fijo de los 3 mapas (grilla de estaciones)

from estaciones import (Despensa, TablaCortar, EstacionCocina,
                        Freidora, Mostrador, EstacionEntrega)
from ingredientes import (INGREDIENTES_SODA_TICA,
                           INGREDIENTES_PIZZERIA, INGREDIENTES_SUSHI)

TAM_CELDA = 60     # Tamaño en píxeles de cada celda del mapa

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
    G = 7      # Número de filas
    C = 11     # Número de columnas
    grid = [[None]*C for _ in range(G)]    # Grilla vacía inicial

    # Fila 0 — pared norte: despensas
    grid[0][1]  = Despensa("Arroz",    0, 1)     # Despensa de arroz
    grid[0][3]  = Despensa("Frijoles", 0, 3)     # Despensa de frijoles
    grid[0][5]  = Despensa("Carne",    0, 5)     # Despensa de carne
    grid[0][7]  = Despensa("Ensalada", 0, 7)     # Despensa de ensalada

    # Fila 1 — mostradores norte
    grid[1][0]  = Mostrador(1, 0)      # Mostrador esquina izquierda
    grid[1][10] = Mostrador(1, 10)     # Mostrador esquina derecha

    # Fila 2 — isla central norte
    grid[2][2]  = TablaCortar(2, 2)         # Tabla de cortar
    grid[2][4]  = TablaCortar(2, 4)         # Tabla de cortar
    grid[2][6]  = EstacionCocina(2, 6)      # Estación de cocina
    grid[2][8]  = Mostrador(2, 8)            # Mostrador

    # Fila 4 — isla central sur
    grid[4][2]  = Mostrador(4, 2)            # Mostrador
    grid[4][4]  = TablaCortar(4, 4)         # Tabla de cortar
    grid[4][6]  = EstacionCocina(4, 6)      # Estación de cocina
    grid[4][8]  = Mostrador(4, 8)            # Mostrador

    # Fila 5 — mostradores sur
    grid[5][0]  = Mostrador(5, 0)            # Mostrador esquina izquierda
    grid[5][10] = Mostrador(5, 10)           # Mostrador esquina derecha

    # Fila 6 — pared sur: entrega
    grid[6][5]  = EstacionEntrega(6, 5)      # Estación de entrega

    pos_chef1 = (3, 1)     # Posición inicial del chef 1
    pos_chef2 = (3, 9)     # Posición inicial del chef 2
    return grid, pos_chef1, pos_chef2, G, C    # Retorna toda la configuración del mapa


def _mapa_pizzeria():
    """
    Mapa 1 — Pizzería Roma  (Medio)
    Grilla 7 filas x 13 cols
    Ingredientes: Masa, Salsa, Queso, Pepperoni, Jamón
    Recetas: Margarita, Pepperoni, Calzone
    """
    G = 7      # Número de filas
    C = 13     # Número de columnas
    grid = [[None]*C for _ in range(G)]    # Grilla vacía inicial

    # Fila 0 — despensas
    grid[0][1]  = Despensa("Masa",      0, 1)     # Despensa de masa
    grid[0][3]  = Despensa("Salsa",     0, 3)     # Despensa de salsa
    grid[0][5]  = Despensa("Queso",     0, 5)     # Despensa de queso
    grid[0][7]  = Despensa("Pepperoni", 0, 7)     # Despensa de pepperoni
    grid[0][9]  = Despensa("Jamón",     0, 9)     # Despensa de jamón

    # Bordes
    grid[1][0]  = Mostrador(1, 0)       # Mostrador esquina izquierda
    grid[1][12] = Mostrador(1, 12)      # Mostrador esquina derecha

    # Isla norte
    grid[2][2]  = TablaCortar(2, 2)         # Tabla de cortar
    grid[2][4]  = TablaCortar(2, 4)         # Tabla de cortar
    grid[2][6]  = EstacionCocina(2, 6)      # Estación de cocina
    grid[2][8]  = EstacionCocina(2, 8)      # Estación de cocina
    grid[2][10] = Mostrador(2, 10)           # Mostrador

    # Isla sur
    grid[4][2]  = Mostrador(4, 2)            # Mostrador
    grid[4][4]  = TablaCortar(4, 4)         # Tabla de cortar
    grid[4][6]  = EstacionCocina(4, 6)      # Estación de cocina
    grid[4][8]  = Mostrador(4, 8)            # Mostrador
    grid[4][10] = Mostrador(4, 10)           # Mostrador

    # Bordes
    grid[5][0]  = Mostrador(5, 0)            # Mostrador esquina izquierda
    grid[5][12] = Mostrador(5, 12)           # Mostrador esquina derecha

    # Entrega
    grid[6][6]  = EstacionEntrega(6, 6)      # Estación de entrega

    pos_chef1 = (3, 1)      # Posición inicial del chef 1
    pos_chef2 = (3, 11)     # Posición inicial del chef 2
    return grid, pos_chef1, pos_chef2, G, C    # Retorna toda la configuración del mapa


def _mapa_sushi():
    """
    Mapa 2 — Sushi Bar Kyoto  (Difícil)
    Grilla 8 filas x 13 cols
    Ingredientes: Arroz, Salmon, Aguacate, Cangrejo, Alga, Tofu
    Recetas: California Roll, Nigiri, Temaki, Miso Soup
    """
    G = 8      # Número de filas
    C = 13     # Número de columnas
    grid = [[None]*C for _ in range(G)]    # Grilla vacía inicial

    # Despensas — fila 0
    grid[0][1]  = Despensa("Arroz",    0, 1)     # Despensa de arroz
    grid[0][3]  = Despensa("Salmón",   0, 3)     # Despensa de salmón
    grid[0][5]  = Despensa("Aguacate", 0, 5)     # Despensa de aguacate
    grid[0][7]  = Despensa("Cangrejo", 0, 7)     # Despensa de cangrejo
    grid[0][9]  = Despensa("Alga",     0, 9)     # Despensa de alga
    grid[0][11] = Despensa("Tofu",     0, 11)    # Despensa de tofu

    # Pared oeste/este
    grid[1][0]  = Mostrador(1, 0)        # Mostrador esquina superior izquierda
    grid[1][12] = Mostrador(1, 12)       # Mostrador esquina superior derecha
    grid[6][0]  = Mostrador(6, 0)        # Mostrador esquina inferior izquierda
    grid[6][12] = Mostrador(6, 12)       # Mostrador esquina inferior derecha

    # Isla norte
    grid[2][2]  = TablaCortar(2, 2)         # Tabla de cortar
    grid[2][4]  = TablaCortar(2, 4)         # Tabla de cortar
    grid[2][6]  = EstacionCocina(2, 6)      # Estación de cocina
    grid[2][8]  = EstacionCocina(2, 8)      # Estación de cocina
    grid[2][10] = Mostrador(2, 10)           # Mostrador

    # Isla central
    grid[4][3]  = Mostrador(4, 3)            # Mostrador
    grid[4][5]  = TablaCortar(4, 5)         # Tabla de cortar
    grid[4][7]  = EstacionCocina(4, 7)      # Estación de cocina
    grid[4][9]  = Mostrador(4, 9)            # Mostrador

    # Isla sur
    grid[6][2]  = Mostrador(6, 2)            # Mostrador
    grid[6][4]  = TablaCortar(6, 4)         # Tabla de cortar
    grid[6][6]  = Mostrador(6, 6)            # Mostrador
    grid[6][8]  = Mostrador(6, 8)            # Mostrador
    grid[6][10] = Mostrador(6, 10)           # Mostrador

    # Entrega
    grid[7][6]  = EstacionEntrega(7, 6)      # Estación de entrega

    pos_chef1 = (3, 1)       # Posición inicial del chef 1
    pos_chef2 = (5, 11)      # Posición inicial del chef 2
    return grid, pos_chef1, pos_chef2, G, C    # Retorna toda la configuración del mapa


MAPAS = [_mapa_soda_tica, _mapa_pizzeria, _mapa_sushi]    # Lista de funciones generadoras de mapa


def cargar_mapa(escenario_idx: int):
    """Retorna (grid, pos_chef1, pos_chef2, filas, cols)."""
    return MAPAS[escenario_idx]()    # Ejecuta la función del mapa correspondiente


def obtener_estacion_entrega(grid):
    """Busca y retorna la EstacionEntrega del grid."""
    for fila in grid:                          # Recorre cada fila del mapa
        for celda in fila:                      # Recorre cada celda de la fila
            if isinstance(celda, EstacionEntrega):   # Si encuentra la estación de entrega
                return celda                          # La retorna
    return None    # Si no se encontró ninguna
