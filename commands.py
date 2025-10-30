# commands.py (v9.1 - Soporte para BeadColorEntry)

from abc import ABC, abstractmethod
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QRect 

# --- Importar BeadColorEntry (asumiendo que models.py está accesible) ---
try:
    from models import BeadColorEntry
except ImportError:
    # Definición dummy para evitar errores de tipo si la importación falla
    class BeadColorEntry:
        def __init__(self, color, finish="Opaque", code=None, name=None): self.color = color; self.finish=finish; self.code=code; self.name=name
        def is_shiny(self): return False
        def __repr__(self): return str(self.color.name())


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
    # MODIFICADO: El diccionario changes ahora usa BeadColorEntry | None
    def __init__(self, grid_canvas, changes: dict[tuple[int, int], tuple[BeadColorEntry | None, BeadColorEntry | None]]):
        self._canvas = grid_canvas 
        # Formato: {(x, y): (old_entry, new_entry)}
        self._changes = changes 

    def execute(self):
        """Aplica las nuevas entradas de color a los datos de la cuadrícula del lienzo."""
        needs_update = False
        for (x, y), (old_entry, new_entry) in self._changes.items():
            if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                
                # Comprobación de cambio: Compara la nueva entrada con la actual
                if self._canvas.grid_data[y][x] != new_entry:
                     self._canvas.grid_data[y][x] = new_entry
                     needs_update = True
                     
        if needs_update:
            self._canvas.update() 

    def undo(self):
        """Restaura las entradas antiguas a los datos de la cuadrícula del lienzo."""
        needs_update = False
        for (x, y), (old_entry, new_entry) in self._changes.items():
             if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                 
                 # Comprobación de cambio: Restaura la entrada antigua
                 if self._canvas.grid_data[y][x] != old_entry:
                      self._canvas.grid_data[y][x] = old_entry
                      needs_update = True
                      
        if needs_update:
            self._canvas.update() 
                
    def merge_with(self, next_command) -> bool:
        """Fusiona dos PaintCommands si son parte del mismo trazo de arrastre."""
        if not isinstance(next_command, PaintCommand) or self._canvas != next_command._canvas:
            return False
        
        # El valor antiguo se mantiene como el primer estado, y el nuevo se actualiza.
        # No necesitamos verificar el tipo de dato, solo las coordenadas.
        for coords, (next_old, next_new) in next_command._changes.items():
            if coords in self._changes:
                 # Mantener el 'old_entry' original, actualizar al 'new_entry' más reciente
                 self._changes[coords] = (self._changes[coords][0], next_new) 
            else:
                 # Añadir nueva entrada al comando actual
                 self._changes[coords] = (next_old, next_new)
        return True

# --- Comando para Cortar, Pegar, Borrar Selección ---
class SelectionCommand(Command):
    """
    Representa una operación en un área seleccionada (Cortar, Pegar, Borrar).
    Almacena los datos *antes* de la operación para deshacer.
    """
    def __init__(self, grid_canvas, selection_rect: QRect, 
                 # MODIFICADO: paste_data ahora es list[list[BeadColorEntry | None]]
                 paste_data: list[list[BeadColorEntry | None]] | None = None):
        """
        Args:
            ...
            paste_data: Si es una operación de Pegar, esta es la data a pegar.
                        Si es None (para Cortar/Borrar), se rellenará con None.
        """
        self._canvas = grid_canvas
        self._rect = selection_rect
        self._paste_data = paste_data
        
        # Almacenará los datos que fueron sobrescritos (list[list[BeadColorEntry | None]])
        self._undone_data: list[list[BeadColorEntry | None]] = [] 

    # MODIFICADO: Extrae BeadColorEntry
    def _get_data_from_rect(self, rect: QRect) -> list[list[BeadColorEntry | None]]:
        """Extrae las entradas de color de un área del lienzo."""
        data = []
        for r in range(rect.height()):
            row = []
            y = rect.y() + r
            if 0 <= y < self._canvas.grid_height:
                for c in range(rect.width()):
                    x = rect.x() + c
                    if 0 <= x < self._canvas.grid_width:
                        # Almacena la entrada completa (BeadColorEntry o None)
                        row.append(self._canvas.grid_data[y][x])
                    else:
                        row.append(None) 
            else:
                row = [None] * rect.width() 
            data.append(row)
        return data

    # MODIFICADO: Aplica BeadColorEntry
    def _apply_data_to_rect(self, rect: QRect, data: list[list[BeadColorEntry | None]]):
        """Aplica un bloque de entradas de color a un área del lienzo."""
        for r, row_data in enumerate(data):
            y = rect.y() + r
            if 0 <= y < self._canvas.grid_height:
                for c, entry in enumerate(row_data):
                    x = rect.x() + c
                    if 0 <= x < self._canvas.grid_width:
                        # Aplica la entrada completa (BeadColorEntry o None)
                        self._canvas.grid_data[y][x] = entry

    def execute(self):
        """Aplica la operación (Pegar, Cortar, Borrar)."""
        self._undone_data = self._get_data_from_rect(self._rect)
        
        if self._paste_data:
            self._apply_data_to_rect(self._rect, self._paste_data)
        else:
            # Crea una matriz de None (borrado)
            empty_data = [[None for _ in range(self._rect.width())] for _ in range(self._rect.height())]
            self._apply_data_to_rect(self._rect, empty_data)
        
        self._canvas.update()
        # NOTA: El retorno de execute ahora es _undone_data (list[list[BeadColorEntry | None]])
        return self._undone_data 

    def undo(self):
        """Restaura los datos que fueron sobrescritos."""
        self._apply_data_to_rect(self._rect, self._undone_data)
        self._canvas.update()

# --- Fin de la clase SelectionCommand ---