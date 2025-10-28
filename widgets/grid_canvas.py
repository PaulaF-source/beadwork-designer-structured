# widgets/grid_canvas.py

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QMouseEvent # Added QMouseEvent
from PyQt6.QtCore import Qt, QPointF, QPoint # Added QPoint for event.position()

# --- GridCanvas class definition goes below ---
class GridCanvas(QWidget):
    """ 
    The main design canvas. Handles both Square and Peyote/Brick grid types,
    cell painting, grid lines, and mirror modes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default values, usually overridden immediately by MainWindow setup
        self.grid_width: int = 30 
        self.grid_height: int = 10
        self.cell_size: int = 12
        self.grid_type: str = "Square"
        self.mirror_mode_horizontal: bool = False
        self.mirror_mode_vertical: bool = False
        self.current_color: QColor = QColor(0, 0, 0, 0) # Default: Eraser

        # Initialize grid data with None
        self.grid_data: list[list[QColor | None]] = self._create_grid(self.grid_width, self.grid_height)

        # Size policy tells the layout how this widget likes to be sized.
        # Preferred means it has a preferred size (calculated in updateGeometry),
        # but it can shrink or expand if needed.
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._update_canvas_size_hint() # Set initial size hint

    # --- Mirror Mode Setters ---
    def set_mirror_mode_horizontal(self, state: int): # state comes from QCheckBox.stateChanged signal
        """Sets the horizontal mirror mode based on checkbox state."""
        self.mirror_mode_horizontal = (state == Qt.CheckState.Checked.value)
        self.update() # Trigger repaint to show/hide mirror line

    def set_mirror_mode_vertical(self, state: int):
        """Sets the vertical mirror mode based on checkbox state."""
        self.mirror_mode_vertical = (state == Qt.CheckState.Checked.value)
        self.update() # Trigger repaint

    # --- Grid Configuration ---
    def _create_grid(self, w: int, h: int) -> list[list[QColor | None]]:
        """Creates a new grid data structure filled with None."""
        # Use type hints for clarity
        return [[None for _ in range(w)] for _ in range(h)]

    def set_grid_type(self, grid_type: str):
        """Sets the grid type ('Square' or 'Peyote/Brick')."""
        if grid_type in ["Square", "Peyote/Brick"]:
            if self.grid_type != grid_type:
                self.grid_type = grid_type
                self._update_canvas_size_hint() # Size hint might change
                self.update() # Trigger repaint

    def set_grid_size(self, w: int, h: int):
        """Sets the grid dimensions and resets grid data."""
        new_w = max(1, w) # Ensure at least 1x1 grid
        new_h = max(1, h)
        if self.grid_width != new_w or self.grid_height != new_h:
            self.grid_width = new_w
            self.grid_height = new_h
            self.grid_data = self._create_grid(self.grid_width, self.grid_height)
            self._update_canvas_size_hint() # Update preferred size for layout
            self.update() # Trigger repaint

    def set_cell_size(self, size: int):
        """Sets the size of each grid cell in pixels."""
        new_size = max(5, size) # Ensure minimum cell size
        if self.cell_size != new_size:
            self.cell_size = new_size
            self._update_canvas_size_hint() # Update preferred size for layout
            self.update() # Trigger repaint

    def _update_canvas_size_hint(self):
        """Updates the widget's preferred size based on current grid config."""
        # Calculate width considering Peyote offset
        width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
        new_width = int(width_multiplier * self.cell_size) + 1 # +1 for the last grid line
        new_height = self.grid_height * self.cell_size + 1 # +1 for the last grid line

        # Set minimum size AND inform the layout system of the preferred size change
        self.setMinimumSize(new_width, new_height) 
        self.updateGeometry() # Crucial call to notify layout managers

    # --- Painting ---
    def set_current_color(self, color: QColor):
        """Sets the color used for painting."""
        self.current_color = color

    def paintEvent(self, event): # event argument is needed by Qt
        """Handles painting the grid background, cells, lines, and mirror guides."""
        painter = QPainter(self)
        # 1. Fill background (use a slightly off-white for better contrast)
        # Consistent with ScrollArea background set in stylesheet
        painter.fillRect(self.rect(), QColor("#e0e0e0")) 

        # 2. Draw filled cells
        for y in range(self.grid_height):
            # Calculate horizontal offset for odd rows in Peyote
            x_offset = self.cell_size / 2 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0
            for x in range(self.grid_width):
                color = self.grid_data[y][x]
                if color: # Only draw if there's a color
                    cell_x = x * self.cell_size + x_offset
                    cell_y = y * self.cell_size
                    painter.fillRect(int(cell_x), int(cell_y), self.cell_size, self.cell_size, QBrush(color))

        # 3. Draw grid lines (use a slightly darker gray)
        pen = QPen(QColor("#b0b0b0"), 1) 
        painter.setPen(pen)

        # Calculate actual drawing boundaries
        width_multiplier_paint = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
        # Adjust max_x calculation for odd row count in Peyote
        max_x_calc = (self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" and self.grid_height > 1 and self.grid_height % 2 != 0 else self.grid_width)
        max_x_paint = max_x_calc * self.cell_size
        max_y_paint = self.grid_height * self.cell_size

        if self.grid_type == "Square":
            # Draw vertical lines
            for x_line in range(self.grid_width + 1): 
                px = x_line * self.cell_size
                painter.drawLine(int(px), 0, int(px), int(max_y_paint))
            # Draw horizontal lines
            for y_line in range(self.grid_height + 1): 
                py = y_line * self.cell_size
                painter.drawLine(0, int(py), int(max_x_paint), int(py))
        else: # Peyote/Brick - Draw individual cell outlines for clarity
             painter.setBrush(Qt.BrushStyle.NoBrush) # No fill for outlines
             for y_line in range(self.grid_height):
                x_offset_line = self.cell_size / 2 if y_line % 2 != 0 else 0
                for x_line in range(self.grid_width): 
                    cell_x_line = x_line * self.cell_size + x_offset_line
                    cell_y_line = y_line * self.cell_size
                    painter.drawRect(int(cell_x_line), int(cell_y_line), self.cell_size, self.cell_size)

        # 4. Draw mirror lines (if active)
        if (self.mirror_mode_horizontal and self.grid_width > 1) or \
           (self.mirror_mode_vertical and self.grid_height > 1):
            mirror_pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
            painter.setPen(mirror_pen)
            # Horizontal mirror line (vertical visual line)
            if self.mirror_mode_horizontal and self.grid_width > 1:
                center_x = (width_multiplier_paint / 2) * self.cell_size 
                painter.drawLine(QPointF(center_x, 0), QPointF(center_x, max_y_paint))
            # Vertical mirror line (horizontal visual line)
            if self.mirror_mode_vertical and self.grid_height > 1:
                center_y = (self.grid_height / 2) * self.cell_size
                # Use max_x_paint for the line end
                painter.drawLine(QPointF(0, center_y), QPointF(max_x_paint, center_y)) 

    # --- Mouse Interaction ---
    def _get_cell_coords_from_pos(self, event_pos: QPoint) -> tuple[int, int] | None:
        """Calculates grid (x, y) coordinates from a mouse position. Returns None if outside."""
        y = int(event_pos.y() // self.cell_size)
        x_offset = self.cell_size / 2 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0
        x = int((event_pos.x() - x_offset) // self.cell_size)

        # Bounds check
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            # Specific check for Peyote horizontal bounds within the cell area
            if self.grid_type == "Peyote/Brick":
                 cell_start_x = x * self.cell_size + x_offset
                 if not (cell_start_x <= event_pos.x() < cell_start_x + self.cell_size):
                     return None # Click was outside the horizontal boundary of the cell
            return x, y
        return None

    def _paint_cell(self, event_pos: QPoint):
        """Paints the cell under the cursor and handles mirror modes."""
        coords = self._get_cell_coords_from_pos(event_pos)
        if coords is None:
            return # Click was outside valid grid area

        x, y = coords

        # Determine color to paint (None for eraser)
        paint_color = None if self.current_color.alpha() == 0 else self.current_color
        needs_update = False

        # --- Mirroring Logic ---
        cells_to_paint: set[tuple[int, int]] = {(x, y)} # Use a set to handle overlaps automatically

        # Calculate potential mirrored coordinates
        mirrored_x = self.grid_width - 1 - x
        mirrored_y = self.grid_height - 1 - y

        # Add horizontally mirrored cell if mode is active and it's a different cell
        if self.mirror_mode_horizontal and mirrored_x != x:
            cells_to_paint.add((mirrored_x, y))
        # Add vertically mirrored cell if mode is active and it's a different cell
        if self.mirror_mode_vertical and mirrored_y != y:
            cells_to_paint.add((x, mirrored_y))
        # Add diagonally mirrored cell if both modes active and it's different
        if self.mirror_mode_horizontal and self.mirror_mode_vertical and mirrored_x != x and mirrored_y != y:
             cells_to_paint.add((mirrored_x, mirrored_y)) 

        # Apply paint color to all target cells
        for px, py in cells_to_paint:
             # Double-check bounds just in case (should be okay due to initial check)
             if 0 <= px < self.grid_width and 0 <= py < self.grid_height: 
                 if self.grid_data[py][px] != paint_color:
                     self.grid_data[py][px] = paint_color
                     needs_update = True # Mark that a repaint is needed

        if needs_update:
            self.update() # Trigger a single repaint if any cell changed

    def mousePressEvent(self, event: QMouseEvent):
        """Handles painting on mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._paint_cell(event.position())
        # Could add right-click handling here later (e.g., color picking)
        # super().mousePressEvent(event) # Not strictly necessary unless we need base behavior

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles painting while dragging the mouse (if left button is held)."""
        if event.buttons() & Qt.MouseButton.LeftButton: # Check if left button is pressed
            self._paint_cell(event.position())
        # super().mouseMoveEvent(event)

    # --- Data Management ---
    def clear_grid(self):
        """Resets all cells in the grid to empty (None)."""
        # Create a new empty grid data structure; avoids modifying in place issues
        self.grid_data = self._create_grid(self.grid_width, self.grid_height)
        self.update() # Trigger repaint

    def get_grid_data(self) -> list[list[str | None]]:
        """Returns the grid data as a list of lists containing hex color strings or None."""
        hex_grid = []
        for row in self.grid_data:
            # Convert QColor to hex name, keep None as None
            hex_row = [color.name() if color else None for color in row]
            hex_grid.append(hex_row)
        return hex_grid

    def load_grid_data(self, hex_grid: list[list[str | None]]) -> bool:
        """Loads grid data from a list of lists containing hex color strings or None."""
        try:
            new_height = len(hex_grid)
            # Handle potentially empty grid data
            if new_height == 0:
                 new_width = 0
            else:
                 # Check width based on the first row, assume others are the same (or handle errors)
                 new_width = len(hex_grid[0]) if hex_grid[0] else 0 

            # Basic validation: Check if dimensions seem plausible (optional)
            # if new_width <= 0 or new_height <= 0: return False

            new_grid_data = []
            for y in range(new_height):
                row_data = hex_grid[y]
                if not isinstance(row_data, list): # Basic row validation
                     print(f"Warning: Invalid row data at index {y}. Skipping row.")
                     # Decide how to handle: skip row, add empty row, or fail load?
                     # Adding empty row for robustness:
                     new_grid_data.append([None] * new_width)
                     continue 

                current_row_len = len(row_data)
                new_row = []
                for x in range(new_width):
                    if x < current_row_len:
                         hex_color = row_data[x]
                         # Convert hex to QColor, keep None as None
                         q_color = None
                         if isinstance(hex_color, str) and hex_color.startswith('#'):
                              temp_color = QColor(hex_color)
                              if temp_color.isValid():
                                   q_color = temp_color
                         new_row.append(q_color)
                    else:
                         new_row.append(None) # Pad shorter rows if necessary
                new_grid_data.append(new_row)

            # If loading seems successful, update internal state
            self.grid_data = new_grid_data
            self.grid_width = new_width
            self.grid_height = new_height
            self._update_canvas_size_hint() # Update size hint based on loaded dimensions
            self.update() # Trigger repaint
            return True

        except Exception as e:
            # Log the error for debugging
            print(f"Error loading grid data: {e}")
            # Optional: Show an error message to the user?
            return False

# --- Fin de la clase GridCanvas ---