# widgets/grid_canvas.py (v8.0 - With Zoom/Pan)

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QMouseEvent, QWheelEvent, # Added QWheelEvent
    QTransform # Added QTransform for easier inverse mapping
) 
from PyQt6.QtCore import Qt, QPointF, QPoint, QRectF # Added QRectF for drawing floats

class GridCanvas(QWidget):
    """ 
    The main design canvas. Handles Square/Peyote grids, painting, mirror modes,
    and now includes Zoom (mouse wheel) and Pan (middle mouse button drag).
    """
    # Define zoom limits and step
    MIN_ZOOM = 0.1
    MAX_ZOOM = 5.0
    ZOOM_STEP = 1.2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Grid properties
        self.grid_width: int = 30 
        self.grid_height: int = 10
        self.cell_size: int = 12
        self.grid_type: str = "Square"
        self.grid_data: list[list[QColor | None]] = self._create_grid(self.grid_width, self.grid_height)
        
        # UI interaction properties
        self.current_color: QColor = QColor(0, 0, 0, 0) 
        self.mirror_mode_horizontal: bool = False
        self.mirror_mode_vertical: bool = False
        
        # --- Zoom/Pan Properties ---
        self.zoom_factor: float = 1.0
        self.pan_offset: QPointF = QPointF(0.0, 0.0) # Offset in screen coordinates
        self.last_pan_pos: QPoint | None = None # Store last mouse pos during panning
        
        # Enable mouse tracking for hover effects if needed later (not strictly for pan)
        # self.setMouseTracking(True) 
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._update_canvas_size_hint()

    # --- Mirror Mode Setters (Unchanged) ---
    def set_mirror_mode_horizontal(self, state: int): 
        self.mirror_mode_horizontal = (state == Qt.CheckState.Checked.value)
        self.update() 
    def set_mirror_mode_vertical(self, state: int):
        self.mirror_mode_vertical = (state == Qt.CheckState.Checked.value)
        self.update() 

    # --- Grid Configuration (Unchanged) ---
    def _create_grid(self, w: int, h: int) -> list[list[QColor | None]]:
        return [[None for _ in range(w)] for _ in range(h)]
    def set_grid_type(self, grid_type: str):
        if grid_type in ["Square", "Peyote/Brick"]:
            if self.grid_type != grid_type:
                self.grid_type = grid_type
                self._update_canvas_size_hint() 
                self.update() 
    def set_grid_size(self, w: int, h: int):
        new_w = max(1, w) 
        new_h = max(1, h)
        if self.grid_width != new_w or self.grid_height != new_h:
            self.grid_width = new_w
            self.grid_height = new_h
            self.grid_data = self._create_grid(self.grid_width, self.grid_height)
            self._update_canvas_size_hint() 
            self.update() 
    def set_cell_size(self, size: int):
        new_size = max(5, size) 
        if self.cell_size != new_size:
            self.cell_size = new_size
            self._update_canvas_size_hint() 
            self.update() 

    # --- Size Hint Calculation (MODIFIED for Zoom) ---
    def _update_canvas_size_hint(self):
        """Updates the widget's preferred size based on current grid config AND zoom."""
        # Calculate base width considering Peyote offset
        base_width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
        # Calculate zoomed dimensions
        zoomed_width = int(base_width_multiplier * self.cell_size * self.zoom_factor) + 1 
        zoomed_height = int(self.grid_height * self.cell_size * self.zoom_factor) + 1
        
        # Set minimum size hint based on zoomed size
        # This tells the QScrollArea how big the content *appears* to be
        self.setMinimumSize(zoomed_width, zoomed_height) 
        self.updateGeometry() # Notify layout system

    # --- Painting (MODIFIED for Zoom/Pan) ---
    def set_current_color(self, color: QColor):
        """Sets the color used for painting."""
        self.current_color = color

    def paintEvent(self, event): 
        """Handles painting with zoom and pan transformations."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) # Usually faster without for grids

        # 1. Fill background (covers entire widget area)
        painter.fillRect(self.rect(), QColor("#e0e0e0")) 

        # --- Apply Transformations ---
        painter.save() # Save current state (no transformation)
        painter.translate(self.pan_offset) # Apply pan offset first
        painter.scale(self.zoom_factor, self.zoom_factor) # Apply zoom
        
        # --- Draw Content (using original cell_size, affected by scale/translate) ---
        # 2. Draw filled cells
        # Performance: Consider drawing only visible cells later if needed
        for y in range(self.grid_height):
            x_offset = self.cell_size / 2 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0
            for x in range(self.grid_width):
                color = self.grid_data[y][x]
                if color: 
                    # Use QRectF for potentially fractional coordinates after transform
                    cell_rect = QRectF(x * self.cell_size + x_offset, y * self.cell_size, self.cell_size, self.cell_size)
                    painter.fillRect(cell_rect, QBrush(color))

        # 3. Draw grid lines (only if zoom is high enough to see them clearly)
        if self.cell_size * self.zoom_factor > 4: # Threshold to avoid clutter when zoomed out
            pen = QPen(QColor("#b0b0b0"), 1) 
            # Make line width appear constant regardless of zoom (1 pixel wide)
            pen.setCosmetic(True) 
            painter.setPen(pen)
            
            # Use floating point coordinates for drawing lines
            max_x_paint_unscaled = (self.grid_width + (0.5 if self.grid_type == "Peyote/Brick" and self.grid_height % 2 != 0 and self.grid_height > 1 else 0.0)) * self.cell_size
            max_y_paint_unscaled = float(self.grid_height * self.cell_size)

            if self.grid_type == "Square":
                for x_line in range(self.grid_width + 1): 
                    px = float(x_line * self.cell_size)
                    painter.drawLine(QPointF(px, 0.0), QPointF(px, max_y_paint_unscaled))
                for y_line in range(self.grid_height + 1): 
                    py = float(y_line * self.cell_size)
                    painter.drawLine(QPointF(0.0, py), QPointF(max_x_paint_unscaled, py))
            else: # Peyote/Brick - Draw cell outlines
                 painter.setBrush(Qt.BrushStyle.NoBrush) 
                 for y_line in range(self.grid_height):
                    x_offset_line = self.cell_size / 2.0 if y_line % 2 != 0 else 0.0
                    for x_line in range(self.grid_width): 
                        cell_x_line = x_line * self.cell_size + x_offset_line
                        cell_y_line = y_line * self.cell_size
                        # Use QRectF for drawing
                        painter.drawRect(QRectF(cell_x_line, cell_y_line, self.cell_size, self.cell_size))

        painter.restore() # Restore state (removes scale/translate)

        # --- Draw Overlays (like mirror lines) - In Widget Coordinates (after restore) ---
        # Calculate visual center lines based on zoomed/panned appearance
        # Note: These calculations determine the line position *on the screen*
        if (self.mirror_mode_horizontal and self.grid_width > 1) or \
           (self.mirror_mode_vertical and self.grid_height > 1):
            mirror_pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
            mirror_pen.setCosmetic(True) # Keep dash line 1px wide
            painter.setPen(mirror_pen)

            # Calculate the unscaled center points
            center_x_unscaled = (self.grid_width / 2.0 + (0.25 if self.grid_type == "Peyote/Brick" else 0.0)) * self.cell_size
            center_y_unscaled = (self.grid_height / 2.0) * self.cell_size

            # Transform these center points to screen coordinates
            transform = QTransform().translate(self.pan_offset.x(), self.pan_offset.y()).scale(self.zoom_factor, self.zoom_factor)
            center_screen = transform.map(QPointF(center_x_unscaled, center_y_unscaled))
            
            # Get transformed corners to determine screen boundaries of the grid
            top_left_screen = transform.map(QPointF(0.0, 0.0))
            # Calculate width/height multipliers based on grid type for correct boundaries
            width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
            max_x_unscaled = width_multiplier * self.cell_size
            max_y_unscaled = self.grid_height * self.cell_size
            bottom_right_screen = transform.map(QPointF(max_x_unscaled, max_y_unscaled))

            # Horizontal mirror line (vertical visual line) - use screen coordinates
            if self.mirror_mode_horizontal and self.grid_width > 1:
                painter.drawLine(QPointF(center_screen.x(), top_left_screen.y()), QPointF(center_screen.x(), bottom_right_screen.y()))
            # Vertical mirror line (horizontal visual line) - use screen coordinates
            if self.mirror_mode_vertical and self.grid_height > 1:
                painter.drawLine(QPointF(top_left_screen.x(), center_screen.y()), QPointF(bottom_right_screen.x(), center_screen.y()))


    # --- Mouse Interaction (MODIFIED for Zoom/Pan) ---
    def _get_scene_pos(self, widget_pos: QPoint) -> QPointF:
        """Converts widget pixel coordinates to scene (grid) coordinates."""
        # Inverse transform: subtract pan offset, then divide by zoom factor
        return (QPointF(widget_pos) - self.pan_offset) / self.zoom_factor

    def _get_widget_pos(self, scene_pos: QPointF) -> QPoint:
         """Converts scene (grid) coordinates back to widget pixel coordinates."""
         # Apply transform: scale by zoom factor, then add pan offset
         return (scene_pos * self.zoom_factor + self.pan_offset).toPoint()


    def _get_cell_coords_from_pos(self, event_pos: QPoint) -> tuple[int, int] | None:
        """Calculates grid (x, y) coordinates from a widget mouse position."""
        # Convert widget pos to scene pos first
        scene_pos = self._get_scene_pos(event_pos)
        
        # Now calculate cell coords based on scene_pos and original cell_size
        y = int(scene_pos.y() // self.cell_size)
        x_offset = self.cell_size / 2.0 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0.0
        x = int((scene_pos.x() - x_offset) // self.cell_size)

        # Bounds check (using grid dimensions)
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            # Specific check for Peyote horizontal bounds within the cell area (in scene coords)
            if self.grid_type == "Peyote/Brick":
                 cell_start_x = x * self.cell_size + x_offset
                 if not (cell_start_x <= scene_pos.x() < cell_start_x + self.cell_size):
                     return None 
            return x, y
        return None

    # _paint_cell remains largely the same, using the coords from _get_cell_coords_from_pos
    def _paint_cell(self, event_pos: QPoint):
        """Paints the cell under the cursor and handles mirror modes."""
        coords = self._get_cell_coords_from_pos(event_pos)
        if coords is None: return 
        x, y = coords
        paint_color = None if self.current_color.alpha() == 0 else self.current_color
        needs_update = False
        cells_to_paint: set[tuple[int, int]] = {(x, y)} 
        mirrored_x = self.grid_width - 1 - x
        mirrored_y = self.grid_height - 1 - y
        if self.mirror_mode_horizontal and mirrored_x != x: cells_to_paint.add((mirrored_x, y))
        if self.mirror_mode_vertical and mirrored_y != y: cells_to_paint.add((x, mirrored_y))
        if self.mirror_mode_horizontal and self.mirror_mode_vertical and mirrored_x != x and mirrored_y != y: cells_to_paint.add((mirrored_x, mirrored_y)) 
        for px, py in cells_to_paint:
             if 0 <= px < self.grid_width and 0 <= py < self.grid_height: 
                 if self.grid_data[py][px] != paint_color:
                     self.grid_data[py][px] = paint_color
                     needs_update = True 
        if needs_update: self.update() 

    # --- Event Handlers for Zoom/Pan ---
    def wheelEvent(self, event: QWheelEvent):
        """Handles mouse wheel scrolling for zooming."""
        mouse_point = event.position() # Position relative to widget
        
        # Calculate scene coordinate under mouse BEFORE zoom
        scene_point_before_zoom = self._get_scene_pos(mouse_point.toPoint()) 
        
        # Determine zoom factor change based on wheel delta
        delta = event.angleDelta().y()
        if delta > 0:
            zoom_factor_delta = self.ZOOM_STEP # Zoom in
        else:
            zoom_factor_delta = 1.0 / self.ZOOM_STEP # Zoom out
            
        # Calculate new zoom factor and clamp it
        new_zoom_factor = self.zoom_factor * zoom_factor_delta
        clamped_zoom_factor = max(self.MIN_ZOOM, min(new_zoom_factor, self.MAX_ZOOM))
        
        # Only proceed if zoom actually changed
        if clamped_zoom_factor != self.zoom_factor:
            # Update pan offset to keep the point under the mouse stationary
            # Formula: new_offset = mouse_point - scene_point_before_zoom * new_zoom
            self.pan_offset = QPointF(mouse_point) - scene_point_before_zoom * clamped_zoom_factor
            self.zoom_factor = clamped_zoom_factor
            
            # Update size hint for scroll area and trigger repaint
            self._update_canvas_size_hint()
            self.update() 

    def mousePressEvent(self, event: QMouseEvent):
        """Handles starting painting (left button) or panning (middle button)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._paint_cell(event.pos()) # Use event.pos() which is QPoint
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.last_pan_pos = event.pos() # Store starting point for panning
            self.setCursor(Qt.CursorShape.ClosedHandCursor) # Change cursor
        # super().mousePressEvent(event) # Not needed unless base class has behavior we want

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles painting while dragging (left button) or panning (middle button)."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._paint_cell(event.pos())
        elif event.buttons() & Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            delta = QPointF(event.pos() - self.last_pan_pos) # Calculate delta as QPointF
            self.pan_offset += delta # Add delta to pan offset
            self.last_pan_pos = event.pos() # Update last position
            self.update() # Trigger repaint
        # super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handles stopping panning."""
        if event.button() == Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            self.last_pan_pos = None # Reset pan tracking
            self.setCursor(Qt.CursorShape.ArrowCursor) # Restore cursor
        # super().mouseReleaseEvent(event)

    # --- Data Management (Unchanged) ---
    def clear_grid(self):
        self.grid_data = self._create_grid(self.grid_width, self.grid_height)
        self.update() 
    def get_grid_data(self) -> list[list[str | None]]:
        # ... (implementation unchanged) ...
        hex_grid = []
        for row in self.grid_data:
            hex_row = [color.name() if color else None for color in row]
            hex_grid.append(hex_row)
        return hex_grid

    def load_grid_data(self, hex_grid: list[list[str | None]]) -> bool:
        # ... (implementation largely unchanged, maybe add zoom/pan reset here?) ...
        try:
            # --- Optional: Reset zoom/pan when loading a new design ---
            # self.zoom_factor = 1.0
            # self.pan_offset = QPointF(0.0, 0.0)
            # --- End Optional Reset ---
            
            new_height = len(hex_grid)
            new_width = 0 if new_height == 0 else (len(hex_grid[0]) if hex_grid[0] else 0) 
            
            new_grid_data = []
            for y in range(new_height):
                row_data = hex_grid[y]
                if not isinstance(row_data, list): 
                     new_grid_data.append([None] * new_width)
                     continue 
                current_row_len = len(row_data)
                new_row = []
                for x in range(new_width):
                    if x < current_row_len:
                         hex_color = row_data[x]
                         q_color = None
                         if isinstance(hex_color, str) and hex_color.startswith('#'):
                              temp_color = QColor(hex_color)
                              if temp_color.isValid(): q_color = temp_color
                         new_row.append(q_color)
                    else: new_row.append(None) 
                new_grid_data.append(new_row)
                
            self.grid_data = new_grid_data
            self.grid_width = new_width
            self.grid_height = new_height
            self._update_canvas_size_hint() 
            self.update() 
            return True
            
        except Exception as e:
            print(f"Error loading grid data: {e}")
            return False

# --- Fin de la clase GridCanvas ---