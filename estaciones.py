# estaciones.py — Clases de estaciones de trabajo

import pygame
from constantes import *
from ingredientes import (
    Ingrediente, VegetalFruta, Proteina, PanYBase, Plato,
    crear_ingrediente, ESTADO_CRUDO, ESTADO_PREPARADO, ESTADO_COCINADO
)


class Estacion:
    """Clase base para todas las estaciones de trabajo."""

    def __init__(self, nombre: str, fila: int, col: int,
                 color: tuple = GRIS_OSC, color2: tuple = GRIS_MED):
        self.nombre = nombre                            # Nombre visible de la estación
        self.fila   = fila                              # Fila en la grilla
        self.col    = col                               # Columna en la grilla
        self.color  = color                             # Color principal
        self.color2 = color2                            # Color secundario/borde
        self.ingrediente_encima: Ingrediente | None = None   # Lo que hay sobre la estación

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return False                                    # Por defecto no acepta nada

    def interactuar(self, chef) -> bool:
        return False                                    # Por defecto no hace nada

    def actualizar(self):
        pass                                             # Por defecto no actualiza nada

    def dibujar(self, surface: pygame.Surface, rect: pygame.Rect, fuente):
        pygame.draw.rect(surface, self.color, rect, border_radius=6)       # Fondo de la estación
        pygame.draw.rect(surface, self.color2, rect, width=2, border_radius=6)  # Borde
        label = fuente.render(self.nombre[:4], True, CREMA)                # Nombre truncado
        surface.blit(label, (rect.centerx - label.get_width() // 2,        # Centrado horizontal
                             rect.centery - label.get_height() // 2))      # Centrado vertical

    def dibujar_progreso(self, surface, rect, progreso, color):
        barra_w = rect.width - 8                                            # Ancho de la barra
        pygame.draw.rect(surface, NEGRO, (rect.x + 4, rect.y - 10, barra_w, 7), border_radius=3)  # Fondo barra
        pygame.draw.rect(surface, color,  (rect.x + 4, rect.y - 10, int(barra_w * progreso), 7), border_radius=3)  # Relleno según progreso


class Despensa(Estacion):
    """Provee un ingrediente específico al chef. Cantidad ilimitada."""

    def __init__(self, nombre_ingrediente: str, fila: int, col: int):
        super().__init__(f"D:{nombre_ingrediente[:5]}", fila, col,
                         color=(60, 100, 60), color2=VERDE)
        self.nombre_ingrediente = nombre_ingrediente    # Qué ingrediente entrega esta despensa

    def interactuar(self, chef) -> bool:
        if chef.ingrediente_en_mano is None:                          # Si el chef tiene la mano libre
            chef.ingrediente_en_mano = crear_ingrediente(self.nombre_ingrediente)  # Le da uno nuevo
            return True                                                # Interacción exitosa
        return False                                                   # No puede tomar más de uno

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (50, 90, 50), rect, border_radius=6)        # Fondo verde oscuro
        pygame.draw.rect(surface, VERDE, rect, width=2, border_radius=6)      # Borde verde
        nombre_corto = self.nombre_ingrediente[:6]                            # Nombre truncado
        label = fuente.render(nombre_corto, True, CREMA)                      # Texto del nombre
        surface.blit(label, (rect.centerx - label.get_width() // 2,           # Centrado horizontal
                             rect.centery - label.get_height() // 2 + 6))     # Centrado vertical (con offset)
        ico = fuente.render("D", True, AMARILLO)                              # Ícono "D" de despensa
        surface.blit(ico, (rect.centerx - ico.get_width() // 2, rect.y + 3))  # Coloca el ícono arriba


class TablaCortar(Estacion):
    """Prepara VegetalFruta. El chef mantiene presionada la tecla de acción."""

    def __init__(self, fila: int, col: int):
        super().__init__("Tabla", fila, col,
                         color=(110, 80, 40), color2=(180, 130, 60))
        self._procesando = False         # Si está en proceso de corte
        self._chef_ref   = None          # Chef que está usando la tabla

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, VegetalFruta) and not ingrediente.esta_listo  # Solo vegetales crudos

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano                       # Lo que trae el chef
        if ing is None:                                       # Si no trae nada
            return False
        if self.puede_aceptar(ing):                           # Si puede procesarse aquí
            self._procesando = True                            # Marca como en proceso
            self._chef_ref   = chef                            # Guarda referencia al chef
            return True
        return False

    def soltar(self):
        self._procesando = False     # Detiene el procesamiento
        self._chef_ref   = None      # Limpia la referencia

    def actualizar(self):
        if self._procesando and self._chef_ref:                 # Si está activa y hay chef
            ing = self._chef_ref.ingrediente_en_mano             # Ingrediente que se procesa
            if ing and not ing.esta_listo:                       # Si aún no está listo
                ing.tick_preparacion()                           # Avanza un frame de corte
            else:
                self._procesando = False                         # Detiene si ya terminó o se fue

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (100, 70, 30), rect, border_radius=6)        # Fondo madera
        pygame.draw.rect(surface, (200, 150, 60), rect, width=2, border_radius=6)  # Borde madera
        label = fuente.render("Tabla", True, CREMA)                             # Etiqueta de la estación
        surface.blit(label, (rect.centerx - label.get_width() // 2,             # Centrado horizontal
                             rect.centery - label.get_height() // 2))          # Centrado vertical
        if self._procesando and self._chef_ref:                                 # Si hay corte en curso
            ing = self._chef_ref.ingrediente_en_mano                            # Ingrediente procesado
            if ing:
                self.dibujar_progreso(surface, rect, ing.progreso_prep(), VERDE)  # Barra de progreso


class EstacionCocina(Estacion):
    """Cocina Proteínas. Se quema si se deja demasiado tiempo."""

    def __init__(self, fila: int, col: int):
        super().__init__("Cocina", fila, col,
                         color=(140, 40, 20), color2=(220, 80, 40))
        self._procesando = False        # Si se está cocinando algo
        self._chef_ref   = None         # Chef que cocina

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, Proteina) and not ingrediente.esta_listo  # Solo proteínas crudas

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano                # Lo que trae el chef
        if ing is None:                                # Si no trae nada
            return False
        if self.puede_aceptar(ing):                    # Si puede cocinarse aquí
            self._procesando = True                     # Marca como en proceso
            self._chef_ref   = chef                      # Guarda referencia al chef
            return True
        return False

    def soltar(self):
        self._procesando = False     # Detiene la cocción
        self._chef_ref   = None      # Limpia la referencia

    def actualizar(self):
        if self._procesando and self._chef_ref:                  # Si hay cocción activa
            ing = self._chef_ref.ingrediente_en_mano               # Ingrediente que se cocina
            if ing and isinstance(ing, Proteina):                   # Verifica tipo correcto
                ing.tick_preparacion()                              # Avanza un frame de cocción
            else:
                self._procesando = False                            # Detiene si ya no aplica

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (120, 30, 10), rect, border_radius=6)            # Fondo rojo oscuro
        pygame.draw.rect(surface, (230, 90, 40), rect, width=2, border_radius=6)   # Borde naranja
        label = fuente.render("Cocina", True, CREMA)                               # Etiqueta
        surface.blit(label, (rect.centerx - label.get_width() // 2,                # Centrado horizontal
                             rect.centery - label.get_height() // 2))             # Centrado vertical
        if self._procesando and self._chef_ref:                                    # Si hay cocción en curso
            ing = self._chef_ref.ingrediente_en_mano                               # Ingrediente cocinado
            if ing and isinstance(ing, Proteina):
                prog  = ing.progreso_prep()                                        # Progreso de cocción
                color = ROJO if prog > 0.75 else NARANJA_VIV                       # Rojo si cerca de quemarse
                self.dibujar_progreso(surface, rect, prog, color)                  # Barra de progreso


class Freidora(Estacion):
    """Fríe ingredientes PanYBase tipo Papas."""

    def __init__(self, fila: int, col: int):
        super().__init__("Freid.", fila, col,
                         color=(160, 130, 20), color2=(230, 200, 60))
        self._procesando = False       # Si se está friendo algo
        self._chef_ref   = None        # Chef que está friendo

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, PanYBase) and ingrediente.nombre == "Papas"  # Solo papas

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano                  # Lo que trae el chef
        if ing and self.puede_aceptar(ing):              # Si es válido para freír
            self._procesando = True                       # Marca como en proceso
            self._chef_ref   = chef                        # Guarda referencia al chef
            return True
        return False

    def soltar(self):
        self._procesando = False     # Detiene la fritura
        self._chef_ref   = None      # Limpia la referencia

    def actualizar(self):
        if self._procesando and self._chef_ref:        # Si hay fritura activa
            ing = self._chef_ref.ingrediente_en_mano      # Ingrediente que se fríe
            if ing:
                ing.tick_preparacion()                     # Avanza un frame de fritura

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (140, 110, 10), rect, border_radius=6)        # Fondo amarillo oscuro
        pygame.draw.rect(surface, AMARILLO, rect, width=2, border_radius=6)     # Borde amarillo
        label = fuente.render("Freid.", True, CREMA)                            # Etiqueta
        surface.blit(label, (rect.centerx - label.get_width() // 2,             # Centrado horizontal
                             rect.centery - label.get_height() // 2))          # Centrado vertical


class Mostrador(Estacion):
    """
    Superficie donde los chefs pueden:
    - Dejar un ingrediente individual (si la mesa está vacía).
    - Combinar varios ingredientes listos en un Plato (dejando uno
      tras otro sobre la mesa).
    - Recoger lo que haya en la mesa (ingrediente suelto o Plato).
    """

    def __init__(self, fila: int, col: int):
        super().__init__("Mesa", fila, col,
                         color=(70, 60, 50), color2=GRIS_MED)
        self.ingrediente_encima = None   # Ingrediente | Plato | None    # Qué hay sobre la mesa

    def interactuar(self, chef) -> bool:
        en_mano = chef.ingrediente_en_mano               # Lo que trae el chef

        # Caso 1: mesa vacía y el chef trae algo → lo deja en la mesa
        if self.ingrediente_encima is None and en_mano is not None:
            self.ingrediente_encima = en_mano             # Deja el ingrediente en la mesa
            chef.ingrediente_en_mano = None               # Vacía la mano del chef
            return True

        # Caso 2: mesa vacía y el chef no trae nada → no hay nada que hacer
        if self.ingrediente_encima is None and en_mano is None:
            return False

        # Caso 3: hay algo en la mesa y el chef no trae nada → lo recoge
        if self.ingrediente_encima is not None and en_mano is None:
            chef.ingrediente_en_mano = self.ingrediente_encima  # El chef recoge lo de la mesa
            self.ingrediente_encima = None                       # La mesa queda vacía
            return True

        # Caso 4: hay algo en la mesa Y el chef trae algo listo →
        # combinarlos en un Plato (esto es lo que permite armar recetas
        # de varios ingredientes, ej. Arroz + Frijoles).
        if self.ingrediente_encima is not None and en_mano is not None:
            if not en_mano.esta_listo:
                return False  # no se puede combinar algo crudo/sin preparar

            existente = self.ingrediente_encima              # Lo que ya había en la mesa

            if isinstance(existente, Plato):                  # Si ya es un plato combinado
                if existente.agregar(en_mano):                 # Intenta añadir el nuevo ingrediente
                    chef.ingrediente_en_mano = None             # Vacía la mano si tuvo éxito
                    return True
                return False

            if not existente.esta_listo:
                return False  # lo que hay en la mesa tampoco está listo

            # Combinar el ingrediente existente + el que trae el chef
            plato = Plato()                                    # Crea un plato nuevo
            plato.agregar(existente)                            # Agrega lo que ya había en la mesa
            if plato.agregar(en_mano):                          # Agrega lo que trae el chef
                self.ingrediente_encima = plato                  # La mesa ahora tiene el plato
                chef.ingrediente_en_mano = None                  # Vacía la mano del chef
                return True
            return False

        return False

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (65, 55, 45), rect, border_radius=6)         # Fondo de la mesa
        pygame.draw.rect(surface, GRIS_MED, rect, width=2, border_radius=6)    # Borde de la mesa
        if self.ingrediente_encima:                                            # Si hay algo encima
            nombre = self.ingrediente_encima.nombre[:9]                        # Nombre truncado
            label  = fuente.render(nombre, True, AMARILLO)                     # Texto en amarillo
        else:
            label = fuente.render("Mesa", True, GRIS_MED)                      # Texto por defecto
        surface.blit(label, (rect.centerx - label.get_width() // 2,            # Centrado horizontal
                             rect.centery - label.get_height() // 2))         # Centrado vertical


class EstacionEntrega(Estacion):
    """Recibe el pedido completo. La Cocina valida contra recetas activas."""

    def __init__(self, fila: int, col: int):
        super().__init__("Entrega", fila, col,
                         color=(30, 80, 160), color2=(80, 150, 230))
        self.ultimo_resultado: str | None = None    # 'ok' | 'fail' | None
        self._feedback_ticks: int = 0                # Tiempo restante mostrando el feedback

    def interactuar(self, chef) -> bool:
        return chef.ingrediente_en_mano is not None   # Solo "acepta" si el chef trae algo

    def mostrar_feedback(self, resultado: str):
        self.ultimo_resultado = resultado    # Guarda si fue éxito o fallo
        self._feedback_ticks  = 90            # Duración del efecto visual

    def actualizar(self):
        if self._feedback_ticks > 0:           # Si el feedback sigue activo
            self._feedback_ticks -= 1          # Reduce su duración
        else:
            self.ultimo_resultado = None        # Limpia el feedback al terminar

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (25, 70, 150), rect, border_radius=6)          # Fondo azul
        pygame.draw.rect(surface, (80, 150, 230), rect, width=2, border_radius=6)  # Borde azul claro
        label = fuente.render("Entr.", True, CREMA)                              # Etiqueta
        surface.blit(label, (rect.centerx - label.get_width() // 2,              # Centrado horizontal
                             rect.centery - label.get_height() // 2))           # Centrado vertical
        if self.ultimo_resultado == 'ok':                                        # Si el último fue éxito
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)                 # Capa semitransparente
            overlay.fill((0, 255, 0, 80))                                        # Verde translúcido
            surface.blit(overlay, rect.topleft)                                  # Dibuja el overlay
        elif self.ultimo_resultado == 'fail':                                    # Si el último fue fallo
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)                 # Capa semitransparente
            overlay.fill((255, 0, 0, 80))                                        # Rojo translúcido
            surface.blit(overlay, rect.topleft)                                  # Dibuja el overlay
            