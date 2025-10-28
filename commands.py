# commands.py

from abc import ABC, abstractmethod
from PyQt6.QtGui import QColor
# --- MODIFICADO: Añadir QRect de QtCore ---
from PyQt6.QtCore import QRect 

class Command(ABC):
    """Clase base abstracta para comandos que soportan deshacer/rehacer."""
    @abstractmethod
    def execute(self):
        """Aplica la acción del comando."""
        pass

    @abstractmethod
    def undo(self):
        """Revierte la acción del comando."""
        pass
        
    def merge_with(self, next_command) -> bool:
        """Intenta fusionar este comando con el siguiente. Devuelve True si se fusiona."""
        return False


class PaintCommand(Command):
    """
    Representa pintar una o más celdas. 
    Maneja clics individuales, arrastres y espejos.
    """
    def __init__(self, grid_canvas, changes: dict[tuple[int, int], tuple[QColor | None, QColor | None]]):
        self._canvas = grid_canvas 
        self._changes = changes # Formato: {(x, y): (old_color, new_color)}

    def execute(self):
        """Aplica los nuevos colores a los datos de la cuadrícula del lienzo."""
        needs_update = False
        for (x, y), (old_color, new_color) in self._changes.items():
            if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                if self._canvas.grid_data[y][x] != new_color:
                     self._canvas.grid_data[y][x] = new_color
                     needs_update = True
        if needs_update:
            self._canvas.update() 

    def undo(self):
        """Restaura los colores antiguos a los datos de la cuadrícula del lienzo."""
        needs_update = False
        for (x, y), (old_color, new_color) in self._changes.items():
             if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                 if self._canvas.grid_data[y][x] != old_color:
                      self._canvas.grid_data[y][x] = old_color
                      needs_update = True
        if needs_update:
            self._canvas.update() 
                
    def merge_with(self, next_command) -> bool:
        """Fusiona dos PaintCommands si son parte del mismo trazo de arrastre."""
        if not isinstance(next_command, PaintCommand) or self._canvas != next_command._canvas:
            return False
        
        for coords, (next_old, next_new) in next_command._changes.items():
            if coords in self._changes:
                 self._changes[coords] = (self._changes[coords][0], next_new) 
            else:
                 self._changes[coords] = (next_old, next_new)
        return True

# --- Comando para Cortar, Pegar, Borrar Selección ---
class SelectionCommand(Command):
    """
    Representa una operación en un área seleccionada (Cortar, Pegar, Borrar).
    Almacena los datos *antes* de la operación para deshacer.
    """
    def __init__(self, grid_canvas, selection_rect: QRect, 
                 paste_data: list[list[QColor | None]] | None = None):
        """
        Args:
            grid_canvas: La instancia del lienzo.
            selection_rect: El QRect (en coordenadas de celda) a afectar.
            paste_data: Si es una operación de Pegar, esta es la data a pegar.
                        Si es None (para Cortar/Borrar), se rellenará con None.
        """
        self._canvas = grid_canvas
        self._rect = selection_rect
        self._paste_data = paste_data
        
        # Almacenará los datos que fueron sobrescritos
        self._undone_data: list[list[QColor | None]] = [] 

    def _get_data_from_rect(self, rect: QRect) -> list[list[QColor | None]]:
        """Extrae los datos de color de un área del lienzo."""
        data = []
        for r in range(rect.height()):
            row = []
            y = rect.y() + r
            if 0 <= y < self._canvas.grid_height:
                for c in range(rect.width()):
                    x = rect.x() + c
                    if 0 <= x < self._canvas.grid_width:
                        row.append(self._canvas.grid_data[y][x])
                    else:
                        row.append(None) 
            else:
                row = [None] * rect.width() 
            data.append(row)
        return data

    def _apply_data_to_rect(self, rect: QRect, data: list[list[QColor | None]]):
        """Aplica un bloque de datos de color a un área del lienzo."""
        for r, row_data in enumerate(data):
            y = rect.y() + r
            if 0 <= y < self._canvas.grid_height:
                for c, color in enumerate(row_data):
                    x = rect.x() + c
                    if 0 <= x < self._canvas.grid_width:
                        self._canvas.grid_data[y][x] = color

    def execute(self):
        """Aplica la operación (Pegar, Cortar, Borrar)."""
        self._undone_data = self._get_data_from_rect(self._rect)
        
        if self._paste_data:
            self._apply_data_to_rect(self._rect, self._paste_data)
        else:
            empty_data = [[None for _ in range(self._rect.width())] for _ in range(self._rect.height())]
            self._apply_data_to_rect(self._rect, empty_data)
        
        self._canvas.update()
        return self._undone_data

    def undo(self):
        """Restaura los datos que fueron sobrescritos."""
        self._apply_data_to_rect(self._rect, self._undone_data)
        self._canvas.update()