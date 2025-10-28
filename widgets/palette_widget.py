# widgets/palette_widget.py (v8.2 - Right-Click Delete Added)

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QMouseEvent 
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPoint

class PaletteWidget(QLabel):
    """
    A widget that draws a grid of colors, handles color selection (left-click),
    and color deletion (right-click for user-added colors).
    """
    colorSelected = pyqtSignal(QColor) # Signal emitted on left-click

    # Class constants for configuration
    PRESET_COLORS = [
        ("#FFD700", "Gold"), ("#C0C0C0", "Silver"), ("#CD7F32", "Bronze"), 
        ("#1C1C1C", "Shiny Black"), ("#FFFDD0", "Creamy White")
    ]
    ROWS = 3; COLS = 15; CELL_SIZE = 30; SPACING = 5
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Internal state
        self.palette_set: set[str] = set() # Stores hex names (#RRGGBB) of colors currently in palette
        self.colors: list[QColor | None] = [None] * (self.ROWS * self.COLS) 
        self.tooltips: list[str | None] = [None] * (self.ROWS * self.COLS)
        self.preset_indices: set[int] = set() # --- NUEVO: Store indices of non-deletable colors ---
        self.next_open_slot: int = 0 # Index where the *next* color will be added
        self.hovered_index: int = -1 # For hover effects
        
        # Calculate and set fixed size
        w = (self.CELL_SIZE * self.COLS) + (self.SPACING * (self.COLS + 1))
        h = (self.CELL_SIZE * self.ROWS) + (self.SPACING * (self.ROWS + 1))
        self.setFixedSize(w, h)
        
        self.setMouseTracking(True) # Enable mouse move events even without buttons pressed
        self.setup_default_palette() # Initialize with defaults
        self.draw_palette() # Initial draw
        
    def setup_default_palette(self):
        """Initializes the palette with eraser and preset colors."""
        total_cells = self.ROWS * self.COLS
        self.colors = [None] * total_cells
        self.tooltips = ["Empty"] * total_cells
        self.palette_set.clear()
        self.preset_indices.clear() # --- NUEVO: Clear preset indices ---
        
        # 1. Add Eraser 
        eraser_color = QColor(0, 0, 0, 0) 
        self.colors[0] = eraser_color
        self.tooltips[0] = "Eraser (Clear cell)"
        self.preset_indices.add(0) # --- NUEVO: Eraser is protected ---
        self.next_open_slot = 1 # Start adding after eraser

        # 2. Add Preset Colors
        for hex_color, name in self.PRESET_COLORS:
            if self.next_open_slot >= total_cells: break 
            color = QColor(hex_color)
            if color.isValid(): 
                self.colors[self.next_open_slot] = color
                self.tooltips[self.next_open_slot] = name
                self.palette_set.add(color.name()) 
                self.preset_indices.add(self.next_open_slot) # --- NUEVO: Mark as preset ---
                self.next_open_slot += 1
            else: print(f"Warning: Preset color '{hex_color}' is invalid.")
            
        # Ensure next_open_slot points correctly even if presets filled the palette
        self.next_open_slot = min(self.next_open_slot, total_cells) 


    def add_color(self, color: QColor):
        """Adds a new color to the next available slot."""
        if not color.isValid() or color.name() in self.palette_set: return 
        
        # --- Logic uses self.next_open_slot (simplest approach for now) ---
        if self.next_open_slot >= len(self.colors):
            print("Palette full. Cannot add more colors.") 
            return 
        
        current_index = self.next_open_slot
        self.colors[current_index] = color
        self.tooltips[current_index] = color.name() 
        self.palette_set.add(color.name())
        
        # Increment next_open_slot, but ensure it doesn't go out of bounds
        self.next_open_slot += 1
        self.next_open_slot = min(self.next_open_slot, self.ROWS * self.COLS)
        
        self.draw_palette() 

    # --- MODIFICADO: draw_palette ahora dibuja huecos consistentemente ---
    def draw_palette(self):
        """Draws the entire palette, including hover effects and empty slots."""
        pixmap = QPixmap(self.size()); pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for r in range(self.ROWS):
            for c in range(self.COLS):
                index = (r * self.COLS) + c
                color = self.colors[index] # Can be QColor or None
                x = self.SPACING + (c * (self.CELL_SIZE + self.SPACING))
                y = self.SPACING + (r * (self.CELL_SIZE + self.SPACING))
                rect = QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)
                is_hovered = (index == self.hovered_index)
                
                if index == 0: # Eraser (protected)
                    pen = QPen(QColor("#f8d7da"), 1, Qt.PenStyle.DashLine); brush = QBrush(QColor("#4f2222"))
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2)
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                    eraser_pen = QPen(QColor("#f8d7da"), 2); painter.setPen(eraser_pen); painter.setBrush(Qt.BrushStyle.NoBrush)
                    margin = 7; painter.drawLine(int(rect.left()+margin), int(rect.top()+margin), int(rect.right()-margin), int(rect.bottom()-margin)); painter.drawLine(int(rect.left()+margin), int(rect.bottom()-margin), int(rect.right()-margin), int(rect.top()+margin))
                elif color is None: # Empty slot (result of deletion or initially empty)
                    pen = QPen(QColor("#777"), 1, Qt.PenStyle.DashLine); brush = QBrush(QColor("#404040"))
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine) # Hover on empty
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                else: # Color slot (preset or user-added)
                    pen = QPen(QColor("#1a1a1a"), 1); brush = QBrush(color)
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2) # Hover on color
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                    
        painter.end(); self.setPixmap(pixmap)

    def _get_index_from_pos(self, pos: QPoint) -> int:
        """Calculates the grid index corresponding to a mouse position."""
        # ... (Implementation unchanged from v8.1) ...
        x, y = pos.x(), pos.y();
        if not (self.SPACING <= x < self.width() - self.SPACING and self.SPACING <= y < self.height() - self.SPACING): return -1
        col_float = (x - self.SPACING) / (self.CELL_SIZE + self.SPACING); row_float = (y - self.SPACING) / (self.CELL_SIZE + self.SPACING)
        if col_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING) or row_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING): return -1
        c = int(col_float); r = int(row_float)
        if 0 <= r < self.ROWS and 0 <= c < self.COLS: return (r * self.COLS) + c
        return -1

    # --- MODIFICADO: mousePressEvent handles Right-Click ---
    def mousePressEvent(self, event: QMouseEvent):
        """Handles left-click (select color) and right-click (delete color)."""
        index = self._get_index_from_pos(event.position())
        
        if index == -1: # Click outside any cell
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # Select color on left-click if cell is not empty
            color = self.colors[index]
            if color is not None:
                self.colorSelected.emit(color) 
                
        elif event.button() == Qt.MouseButton.RightButton:
            # Delete color on right-click if it's a user-added color
            if index not in self.preset_indices and self.colors[index] is not None:
                color_to_delete = self.colors[index]
                if color_to_delete: # Should always be true here, but extra safe check
                    color_name = color_to_delete.name()
                    if color_name in self.palette_set:
                         self.palette_set.remove(color_name) # Remove from set
                         
                self.colors[index] = None # Clear the slot in the list
                self.tooltips[index] = "Empty" # Reset tooltip
                
                # --- NOTE: We leave a gap. self.next_open_slot is NOT changed. ---
                # Future improvements could involve shifting items or finding the first gap in add_color.
                
                self.draw_palette() # Redraw to show the empty slot
                # Reset hover index as the cell content changed
                if self.hovered_index == index:
                     self.hovered_index = -1 
                     self.setCursor(Qt.CursorShape.ArrowCursor) # Reset cursor immediately
                     self.setToolTip("")

        super().mousePressEvent(event) # Call base class handler

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles hover effects and tooltips."""
        # ... (Implementation unchanged from v8.1) ...
        index = self._get_index_from_pos(event.position());
        if index != self.hovered_index: self.hovered_index = index; self.draw_palette()
        tooltip_to_show = ""; cursor_to_show = Qt.CursorShape.ArrowCursor
        if index != -1:
            tooltip_to_show = self.tooltips[index] if self.tooltips[index] else "Empty" # Ensure tooltip is str
            if self.colors[index] is not None: cursor_to_show = Qt.CursorShape.PointingHandCursor
        self.setToolTip(tooltip_to_show); self.setCursor(cursor_to_show); super().mouseMoveEvent(event)

    def leaveEvent(self, event): 
        """Clears hover effect when the mouse leaves the widget."""
        # ... (Implementation unchanged from v8.1) ...
        if self.hovered_index != -1: self.hovered_index = -1; self.draw_palette(); self.setToolTip(""); self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def load_palette(self, color_hex_list: list[str]):
        """Loads colors from a list of hex strings."""
        # ... (Implementation unchanged from v8.1, relies on add_color) ...
        self.setup_default_palette() 
        for hex_color in color_hex_list:
            if isinstance(hex_color, str) and hex_color.startswith('#') and len(hex_color) in [7, 9]: 
                q_color = QColor(hex_color)
                if q_color.isValid() and q_color.name() not in self.palette_set: self.add_color(q_color)
            elif isinstance(hex_color, QColor):
                 if hex_color.isValid() and hex_color.name() not in self.palette_set: self.add_color(hex_color)

    def get_palette_data(self) -> list[str]:
        """Returns a list of hex strings for non-preset colors."""
        # ... (Implementation unchanged from v8.1) ...
        added_colors = []; preset_names = set(QColor(hex).name() for hex, name in self.PRESET_COLORS if QColor(hex).isValid()); preset_names.add(QColor(0,0,0,0).name()) 
        # Iterate through the *entire* list now, as colors might have gaps
        for i in range(len(self.colors)): 
             color = self.colors[i]
             if color and color.isValid() and i not in self.preset_indices: # Check against preset_indices
                 added_colors.append(color.name()) 
        return added_colors

# --- Fin de la clase PaletteWidget ---