# widgets/palette_widget.py

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QMouseEvent # Added QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPoint # Added QPoint for _get_index_from_pos

# --- PaletteWidget class definition goes below ---
class PaletteWidget(QLabel):
    colorSelected = pyqtSignal(QColor)
    # --- Good Practice: Define constants within the class or import them ---
    # Using class attributes for constants related to the widget itself
    PRESET_COLORS = [
        ("#FFD700", "Gold"), 
        ("#C0C0C0", "Silver"), 
        ("#CD7F32", "Bronze"), 
        ("#1C1C1C", "Shiny Black"), 
        ("#FFFDD0", "Creamy White")
    ]
    ROWS = 3
    COLS = 15
    CELL_SIZE = 30
    SPACING = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use self. for class constants for clarity
        self.palette_set = set()
        self.colors = [None] * (self.ROWS * self.COLS) 
        self.tooltips = [None] * (self.ROWS * self.COLS)
        self.next_open_slot = 0
        self.hovered_index = -1 # Index of the currently hovered cell

        # Calculate fixed size based on constants
        w = (self.CELL_SIZE * self.COLS) + (self.SPACING * (self.COLS + 1))
        h = (self.CELL_SIZE * self.ROWS) + (self.SPACING * (self.ROWS + 1))
        self.setFixedSize(w, h)

        self.setMouseTracking(True) # Essential for hover effects and tooltips
        self.setup_default_palette()
        self.draw_palette() # Initial drawing

    def setup_default_palette(self):
        """Initializes the palette with eraser and preset colors."""
        self.colors = [None] * (self.ROWS * self.COLS)
        self.tooltips = ["Empty"] * (self.ROWS * self.COLS)
        self.palette_set.clear()

        # Add Eraser (Transparent color)
        eraser_color = QColor(0, 0, 0, 0) 
        self.colors[0] = eraser_color
        self.tooltips[0] = "Eraser (Clear cell)"
        self.next_open_slot = 1

        # Add Preset Colors
        for hex_color, name in self.PRESET_COLORS:
            if self.next_open_slot >= len(self.colors): break # Stop if palette is full
            color = QColor(hex_color)
            if color.isValid(): # Ensure color is valid before adding
                self.colors[self.next_open_slot] = color
                self.tooltips[self.next_open_slot] = name
                self.palette_set.add(color.name()) # Store color name (hex #RRGGBB)
                self.next_open_slot += 1
            else:
                print(f"Warning: Preset color '{hex_color}' is invalid.")

    def add_color(self, color: QColor):
        """Adds a new color to the next available slot if it's not a duplicate."""
        # Check if color is valid and not already present
        if not color.isValid() or color.name() in self.palette_set:
            return 

        # Check if there is space left
        if self.next_open_slot >= len(self.colors):
            print("Palette full. Cannot add more colors.") # Maybe show a status message later
            return 

        # Add the color
        self.colors[self.next_open_slot] = color
        self.tooltips[self.next_open_slot] = color.name() # Use hex name as default tooltip
        self.palette_set.add(color.name())
        self.next_open_slot += 1

        self.draw_palette() # Redraw the palette to show the new color

    def draw_palette(self):
        """Draws the entire palette onto the QLabel's pixmap."""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent) # Transparent background for the drawing itself
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for r in range(self.ROWS):
            for c in range(self.COLS):
                index = (r * self.COLS) + c
                color = self.colors[index]
                # Calculate cell rectangle
                x = self.SPACING + (c * (self.CELL_SIZE + self.SPACING))
                y = self.SPACING + (r * (self.CELL_SIZE + self.SPACING))
                rect = QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)

                is_hovered = (index == self.hovered_index)

                # --- Draw based on cell type ---
                if index == 0: # Eraser
                    # Base style
                    pen = QPen(QColor("#f8d7da"), 1, Qt.PenStyle.DashLine)
                    brush = QBrush(QColor("#4f2222"))
                    # Hover style
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2) # White border on hover

                    painter.setPen(pen)
                    painter.setBrush(brush)
                    painter.drawRoundedRect(rect, 4, 4)

                    # Draw 'X' symbol for eraser
                    eraser_pen = QPen(QColor("#f8d7da"), 2) 
                    painter.setPen(eraser_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    margin = 7 # Margin for the 'X'
                    painter.drawLine(int(rect.left() + margin), int(rect.top() + margin), int(rect.right() - margin), int(rect.bottom() - margin))
                    painter.drawLine(int(rect.left() + margin), int(rect.bottom() - margin), int(rect.right() - margin), int(rect.top() + margin))

                elif color is None: # Empty slot
                    pen = QPen(QColor("#777"), 1, Qt.PenStyle.DashLine)
                    brush = QBrush(QColor("#404040"))
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine)

                    painter.setPen(pen)
                    painter.setBrush(brush)
                    painter.drawRoundedRect(rect, 4, 4)

                else: # Color slot
                    pen = QPen(QColor("#1a1a1a"), 1) # Thin dark border
                    brush = QBrush(color)
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2) # White border on hover

                    painter.setPen(pen)
                    painter.setBrush(brush)
                    painter.drawRoundedRect(rect, 4, 4)

        painter.end()
        self.setPixmap(pixmap) # Update the QLabel content

    def _get_index_from_pos(self, pos: QPoint) -> int:
        """Calculates the grid index corresponding to a mouse position."""
        x, y = pos.x(), pos.y()

        # Quick check if outside the main grid area (including outer spacing)
        if not (self.SPACING <= x < self.width() - self.SPACING and self.SPACING <= y < self.height() - self.SPACING):
             return -1

        # Calculate potential row/col based on float division
        col_float = (x - self.SPACING) / (self.CELL_SIZE + self.SPACING)
        row_float = (y - self.SPACING) / (self.CELL_SIZE + self.SPACING)

        # Check if the click is in the spacing *between* cells
        # col_float % 1 gives the fractional part (position within the cell+spacing unit)
        # We compare this fraction to the proportion the cell takes up in that unit
        if col_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING) or \
           row_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING):
            return -1 # Click was in the spacing

        # Valid click within a cell area, get integer row/col
        c = int(col_float)
        r = int(row_float)

        # Final bounds check
        if 0 <= r < self.ROWS and 0 <= c < self.COLS:
            return (r * self.COLS) + c

        return -1 # Should not happen if logic is correct, but safer

    def mousePressEvent(self, event: QMouseEvent):
        """Handles clicks on palette cells."""
        if event.button() == Qt.MouseButton.LeftButton:
            index = self._get_index_from_pos(event.position())
            if index != -1 and self.colors[index] is not None:
                self.colorSelected.emit(self.colors[index]) # Emit signal if a valid color is clicked
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles hover effects and tooltips."""
        index = self._get_index_from_pos(event.position())

        # If hover index changed, update and redraw
        if index != self.hovered_index:
            self.hovered_index = index
            self.draw_palette() # Redraw needed to show hover effect

        # Set tooltip and cursor based on the hovered cell
        tooltip_to_show = ""
        cursor_to_show = Qt.CursorShape.ArrowCursor
        if index != -1:
            tooltip_to_show = self.tooltips[index]
            if self.colors[index] is not None: # Only show pointing hand if it's a selectable color
                 cursor_to_show = Qt.CursorShape.PointingHandCursor

        self.setToolTip(tooltip_to_show)
        self.setCursor(cursor_to_show)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event): # Use QEvent or specific type if known
        """Clears hover effect when the mouse leaves the widget."""
        if self.hovered_index != -1:
            self.hovered_index = -1
            self.draw_palette() # Redraw to remove hover effect
            self.setToolTip("") # Clear tooltip
            self.setCursor(Qt.CursorShape.ArrowCursor) # Reset cursor
        super().leaveEvent(event)

    def load_palette(self, color_hex_list: list[str]):
        """Loads colors from a list of hex strings, resetting presets first."""
        self.setup_default_palette() # Reset to defaults
        for hex_color in color_hex_list:
            # Basic validation
            if isinstance(hex_color, str) and hex_color.startswith('#') and len(hex_color) in [7, 9]: # #RRGGBB or #AARRGGBB
                q_color = QColor(hex_color)
                # Add only if valid and not already a preset
                if q_color.isValid() and q_color.name() not in self.palette_set:
                    self.add_color(q_color)
            # Allow loading QColor objects directly if needed (e.g., internal use)
            elif isinstance(hex_color, QColor):
                 if hex_color.isValid() and hex_color.name() not in self.palette_set:
                      self.add_color(hex_color)
        # No need to redraw here, add_color already does it.
        # self.draw_palette() # Redundant

    def get_palette_data(self) -> list[str]:
        """Returns a list of hex strings for non-preset colors currently in the palette."""
        added_colors = []
        # Create a set of preset color names (hex #RRGGBB) for quick lookup
        preset_names = set(QColor(hex).name() for hex, name in self.PRESET_COLORS if QColor(hex).isValid())
        # Add eraser's "color name" to avoid saving it
        preset_names.add(QColor(0,0,0,0).name()) 

        # Iterate only up to the next open slot
        for i in range(self.next_open_slot):
             color = self.colors[i]
             # Ensure the color exists, is valid, and is not a preset
             if color and color.isValid() and color.name() not in preset_names:
                 added_colors.append(color.name()) # Append the hex name
        return added_colors

# --- Fin de la clase PaletteWidget ---