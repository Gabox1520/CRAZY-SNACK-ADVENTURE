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
        self.nombre = nombre
        self.fila   = fila
        self.col    = col
        self.color  = color
        self.color2 = color2
        self.ingrediente_encima: Ingrediente | None = None

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return False

    def interactuar(self, chef) -> bool:
        return False

    def actualizar(self):
        pass

    def dibujar(self, surface: pygame.Surface, rect: pygame.Rect, fuente):
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        pygame.draw.rect(surface, self.color2, rect, width=2, border_radius=6)
        label = fuente.render(self.nombre[:4], True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))

    def dibujar_progreso(self, surface, rect, progreso, color):
        barra_w = rect.width - 8
        pygame.draw.rect(surface, NEGRO, (rect.x + 4, rect.y - 10, barra_w, 7), border_radius=3)
        pygame.draw.rect(surface, color,  (rect.x + 4, rect.y - 10, int(barra_w * progreso), 7), border_radius=3)


class Despensa(Estacion):
    """Provee un ingrediente específico al chef. Cantidad ilimitada."""

    def __init__(self, nombre_ingrediente: str, fila: int, col: int):
        super().__init__(f"D:{nombre_ingrediente[:5]}", fila, col,
                         color=(60, 100, 60), color2=VERDE)
        self.nombre_ingrediente = nombre_ingrediente

    def interactuar(self, chef) -> bool:
        if chef.ingrediente_en_mano is None:
            chef.ingrediente_en_mano = crear_ingrediente(self.nombre_ingrediente)
            return True
        return False

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (50, 90, 50), rect, border_radius=6)
        pygame.draw.rect(surface, VERDE, rect, width=2, border_radius=6)
        nombre_corto = self.nombre_ingrediente[:6]
        label = fuente.render(nombre_corto, True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2 + 6))
        ico = fuente.render("D", True, AMARILLO)
        surface.blit(ico, (rect.centerx - ico.get_width() // 2, rect.y + 3))


class TablaCortar(Estacion):
    """Prepara VegetalFruta. El chef mantiene presionada la tecla de acción."""

    def __init__(self, fila: int, col: int):
        super().__init__("Tabla", fila, col,
                         color=(110, 80, 40), color2=(180, 130, 60))
        self._procesando = False
        self._chef_ref   = None

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, VegetalFruta) and not ingrediente.esta_listo

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano
        if ing is None:
            return False
        if self.puede_aceptar(ing):
            self._procesando = True
            self._chef_ref   = chef
            return True
        return False

    def soltar(self):
        self._procesando = False
        self._chef_ref   = None

    def actualizar(self):
        if self._procesando and self._chef_ref:
            ing = self._chef_ref.ingrediente_en_mano
            if ing and not ing.esta_listo:
                ing.tick_preparacion()
            else:
                self._procesando = False

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (100, 70, 30), rect, border_radius=6)
        pygame.draw.rect(surface, (200, 150, 60), rect, width=2, border_radius=6)
        label = fuente.render("Tabla", True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))
        if self._procesando and self._chef_ref:
            ing = self._chef_ref.ingrediente_en_mano
            if ing:
                self.dibujar_progreso(surface, rect, ing.progreso_prep(), VERDE)


class EstacionCocina(Estacion):
    """Cocina Proteínas. Se quema si se deja demasiado tiempo."""

    def __init__(self, fila: int, col: int):
        super().__init__("Cocina", fila, col,
                         color=(140, 40, 20), color2=(220, 80, 40))
        self._procesando = False
        self._chef_ref   = None

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, Proteina) and not ingrediente.esta_listo

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano
        if ing is None:
            return False
        if self.puede_aceptar(ing):
            self._procesando = True
            self._chef_ref   = chef
            return True
        return False

    def soltar(self):
        self._procesando = False
        self._chef_ref   = None

    def actualizar(self):
        if self._procesando and self._chef_ref:
            ing = self._chef_ref.ingrediente_en_mano
            if ing and isinstance(ing, Proteina):
                ing.tick_preparacion()
            else:
                self._procesando = False

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (120, 30, 10), rect, border_radius=6)
        pygame.draw.rect(surface, (230, 90, 40), rect, width=2, border_radius=6)
        label = fuente.render("Cocina", True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))
        if self._procesando and self._chef_ref:
            ing = self._chef_ref.ingrediente_en_mano
            if ing and isinstance(ing, Proteina):
                prog  = ing.progreso_prep()
                color = ROJO if prog > 0.75 else NARANJA_VIV
                self.dibujar_progreso(surface, rect, prog, color)


class Freidora(Estacion):
    """Fríe ingredientes PanYBase tipo Papas."""

    def __init__(self, fila: int, col: int):
        super().__init__("Freid.", fila, col,
                         color=(160, 130, 20), color2=(230, 200, 60))
        self._procesando = False
        self._chef_ref   = None

    def puede_aceptar(self, ingrediente: Ingrediente) -> bool:
        return isinstance(ingrediente, PanYBase) and ingrediente.nombre == "Papas"

    def interactuar(self, chef) -> bool:
        ing = chef.ingrediente_en_mano
        if ing and self.puede_aceptar(ing):
            self._procesando = True
            self._chef_ref   = chef
            return True
        return False

    def soltar(self):
        self._procesando = False
        self._chef_ref   = None

    def actualizar(self):
        if self._procesando and self._chef_ref:
            ing = self._chef_ref.ingrediente_en_mano
            if ing:
                ing.tick_preparacion()

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (140, 110, 10), rect, border_radius=6)
        pygame.draw.rect(surface, AMARILLO, rect, width=2, border_radius=6)
        label = fuente.render("Freid.", True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))


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
        self.ingrediente_encima = None   # Ingrediente | Plato | None

    def interactuar(self, chef) -> bool:
        en_mano = chef.ingrediente_en_mano

        # Caso 1: mesa vacía y el chef trae algo → lo deja en la mesa
        if self.ingrediente_encima is None and en_mano is not None:
            self.ingrediente_encima = en_mano
            chef.ingrediente_en_mano = None
            return True

        # Caso 2: mesa vacía y el chef no trae nada → no hay nada que hacer
        if self.ingrediente_encima is None and en_mano is None:
            return False

        # Caso 3: hay algo en la mesa y el chef no trae nada → lo recoge
        if self.ingrediente_encima is not None and en_mano is None:
            chef.ingrediente_en_mano = self.ingrediente_encima
            self.ingrediente_encima = None
            return True

        # Caso 4: hay algo en la mesa Y el chef trae algo listo →
        # combinarlos en un Plato (esto es lo que permite armar recetas
        # de varios ingredientes, ej. Arroz + Frijoles).
        if self.ingrediente_encima is not None and en_mano is not None:
            if not en_mano.esta_listo:
                return False  # no se puede combinar algo crudo/sin preparar

            existente = self.ingrediente_encima

            if isinstance(existente, Plato):
                if existente.agregar(en_mano):
                    chef.ingrediente_en_mano = None
                    return True
                return False

            if not existente.esta_listo:
                return False  # lo que hay en la mesa tampoco está listo

            # Combinar el ingrediente existente + el que trae el chef
            plato = Plato()
            plato.agregar(existente)
            if plato.agregar(en_mano):
                self.ingrediente_encima = plato
                chef.ingrediente_en_mano = None
                return True
            return False

        return False

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (65, 55, 45), rect, border_radius=6)
        pygame.draw.rect(surface, GRIS_MED, rect, width=2, border_radius=6)
        if self.ingrediente_encima:
            nombre = self.ingrediente_encima.nombre[:9]
            label  = fuente.render(nombre, True, AMARILLO)
        else:
            label = fuente.render("Mesa", True, GRIS_MED)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))


class EstacionEntrega(Estacion):
    """Recibe el pedido completo. La Cocina valida contra recetas activas."""

    def __init__(self, fila: int, col: int):
        super().__init__("Entrega", fila, col,
                         color=(30, 80, 160), color2=(80, 150, 230))
        self.ultimo_resultado: str | None = None
        self._feedback_ticks: int = 0

    def interactuar(self, chef) -> bool:
        return chef.ingrediente_en_mano is not None

    def mostrar_feedback(self, resultado: str):
        self.ultimo_resultado = resultado
        self._feedback_ticks  = 90

    def actualizar(self):
        if self._feedback_ticks > 0:
            self._feedback_ticks -= 1
        else:
            self.ultimo_resultado = None

    def dibujar(self, surface, rect, fuente):
        pygame.draw.rect(surface, (25, 70, 150), rect, border_radius=6)
        pygame.draw.rect(surface, (80, 150, 230), rect, width=2, border_radius=6)
        label = fuente.render("Entr.", True, CREMA)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))
        if self.ultimo_resultado == 'ok':
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 80))
            surface.blit(overlay, rect.topleft)
        elif self.ultimo_resultado == 'fail':
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            surface.blit(overlay, rect.topleft)
            