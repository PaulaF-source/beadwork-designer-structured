# commands.py
from abc import ABC, abstractmethod
from PyQt6.QtGui import QColor

class Command(ABC):
    """Abstract base class for commands supporting undo/redo."""
    @abstractmethod
    def execute(self):
        """Applies the command's action."""
        pass

    @abstractmethod
    def undo(self):
        """Reverts the command's action."""
        pass

# --- Specific Command for Painting ---
class PaintCommand(Command):
    """
    Represents painting one or more cells. 
    Handles single clicks, drags, and mirroring.
    Stores a dictionary of { (x, y): (old_color, new_color) }
    """
    def __init__(self, grid_canvas, changes: dict[tuple[int, int], tuple[QColor | None, QColor | None]]):
        # Store reference to the canvas to modify its data
        self._canvas = grid_canvas 
        # Store all changes made by this single paint operation (could be multiple cells due to mirroring)
        self._changes = changes # Format: {(x, y): (old_color, new_color)}

    def execute(self):
        """Applies the new colors to the canvas grid data."""
        needs_update = False
        for (x, y), (old_color, new_color) in self._changes.items():
            # Check bounds just in case, though they should be valid if generated correctly
            if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                if self._canvas.grid_data[y][x] != new_color:
                     self._canvas.grid_data[y][x] = new_color
                     needs_update = True
        if needs_update:
            self._canvas.update() # Trigger repaint after applying changes

    def undo(self):
        """Restores the old colors to the canvas grid data."""
        needs_update = False
        for (x, y), (old_color, new_color) in self._changes.items():
             if 0 <= x < self._canvas.grid_width and 0 <= y < self._canvas.grid_height:
                 if self._canvas.grid_data[y][x] != old_color:
                      self._canvas.grid_data[y][x] = old_color
                      needs_update = True
        if needs_update:
            self._canvas.update() # Trigger repaint after reverting changes

    # --- Optional: Merging for drag operations ---
    def merge_with(self, next_command) -> bool:
        """
        Checks if this command can be merged with the next one.
        Useful for drag painting, treating it as a single undo step.
        Merges if the next command is also a PaintCommand.
        """
        if not isinstance(next_command, PaintCommand) or self._canvas != next_command._canvas:
            return False

        # Add changes from the next command to this one.
        # If a cell is painted multiple times in a drag, the *original* old_color
        # from `self` is preserved, and the *final* new_color from `next_command` is used.
        for coords, (next_old, next_new) in next_command._changes.items():
            if coords in self._changes:
                # Cell already modified in this drag stroke, update only the 'new_color'
                _ , current_new = self._changes[coords]
                # Only update if the final color actually changes
                if current_new != next_new:
                     self._changes[coords] = (self._changes[coords][0], next_new) # Keep original old, use latest new
            else:
                # First time this cell is modified in this drag stroke
                 self._changes[coords] = (next_old, next_new)
        return True

# --- Future commands (example) ---
# class ClearGridCommand(Command): ...
# class ResizeCommand(Command): ...