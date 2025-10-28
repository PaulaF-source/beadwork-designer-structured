# widgets/grid_canvas.py (v8.2 - Removed slots)

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QMouseEvent, QWheelEvent, QTransform 
) 
from PyQt6.QtCore import Qt, QPointF, QPoint, QRectF, pyqtSignal 

# --- Import Command classes ---
from commands import Command, PaintCommand 

class GridCanvas(QWidget):
    """ 
    The main design canvas. Handles grids, painting, mirror modes, Zoom/Pan,
    and Undo/Redo. Mirror modes are now set via boolean properties.
    """
    undo_redo_changed = pyqtSignal(bool, bool) 

    MIN_ZOOM = 0.1; MAX_ZOOM = 5.0; ZOOM_STEP = 1.2

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
        # --- MODIFICADO: Estos booleanos ahora son la API pública ---
        self.mirror_mode_horizontal: bool = False
        self.mirror_mode_vertical: bool = False
        
        # Zoom/Pan Properties
        self.zoom_factor: float = 1.0
        self.pan_offset: QPointF = QPointF(0.0, 0.0) 
        self.last_pan_pos: QPoint | None = None 
        
        # Undo/Redo Stacks
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self._is_dragging_paint = False 
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._update_canvas_size_hint()

    # --- MODIFICADO: Slots set_mirror_mode_... ELIMINADOS ---
    # (La MainWindow ahora establecerá las propiedades booleanas directamente)

    # --- Grid Configuration (Unchanged) ---
    def _create_grid(self, w: int, h: int) -> list[list[QColor | None]]: 
        # ... (código sin cambios)
        return [[None for _ in range(w)] for _ in range(h)]
    
    def set_grid_type(self, grid_type: str): 
        # ... (código sin cambios)
        if grid_type in ["Square", "Peyote/Brick"]: 
            if self.grid_type != grid_type: self.grid_type = grid_type; self._clear_history(); self._update_canvas_size_hint(); self.update() 
    
    def set_grid_size(self, w: int, h: int):
        # ... (código sin cambios)
        new_w = max(1, w); new_h = max(1, h)
        if self.grid_width != new_w or self.grid_height != new_h: 
            self.grid_width = new_w; self.grid_height = new_h
            self.grid_data = self._create_grid(self.grid_width, self.grid_height)
            self._clear_history(); self._update_canvas_size_hint(); self.update() 
    
    def set_cell_size(self, size: int):
        # ... (código sin cambios)
        new_size = max(5, size) 
        if self.cell_size != new_size: self.cell_size = new_size; self._update_canvas_size_hint(); self.update() 

    # --- Size Hint (Unchanged) ---
    def _update_canvas_size_hint(self):
        # ... (código sin cambios)
        base_width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
        zoomed_width = int(base_width_multiplier * self.cell_size * self.zoom_factor) + 1 
        zoomed_height = int(self.grid_height * self.cell_size * self.zoom_factor) + 1
        self.setMinimumSize(zoomed_width, zoomed_height); self.updateGeometry() 

    # --- Painting (Unchanged) ---
    def set_current_color(self, color: QColor): 
        # ... (código sin cambios)
        self.current_color = color
        
    def paintEvent(self, event): 
        # ... (La lógica de paintEvent ya usa los booleanos self.mirror_mode_...)
        # ... (Así que no se necesita ningún cambio aquí)
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) 
        painter.fillRect(self.rect(), QColor("#e0e0e0")) 
        painter.save(); painter.translate(self.pan_offset); painter.scale(self.zoom_factor, self.zoom_factor) 
        for y in range(self.grid_height):
            x_offset = self.cell_size / 2 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0
            for x in range(self.grid_width):
                color = self.grid_data[y][x]
                if color: cell_rect = QRectF(x * self.cell_size + x_offset, y * self.cell_size, self.cell_size, self.cell_size); painter.fillRect(cell_rect, QBrush(color))
        if self.cell_size * self.zoom_factor > 4: 
            pen = QPen(QColor("#b0b0b0"), 1); pen.setCosmetic(True); painter.setPen(pen)
            max_x_paint_unscaled = (self.grid_width + (0.5 if self.grid_type == "Peyote/Brick" and self.grid_height % 2 != 0 and self.grid_height > 1 else 0.0)) * self.cell_size
            max_y_paint_unscaled = float(self.grid_height * self.cell_size)
            if self.grid_type == "Square":
                for x_line in range(self.grid_width + 1): px = float(x_line * self.cell_size); painter.drawLine(QPointF(px, 0.0), QPointF(px, max_y_paint_unscaled))
                for y_line in range(self.grid_height + 1): py = float(y_line * self.cell_size); painter.drawLine(QPointF(0.0, py), QPointF(max_x_paint_unscaled, py))
            else: 
                 painter.setBrush(Qt.BrushStyle.NoBrush) 
                 for y_line in range(self.grid_height):
                    x_offset_line = self.cell_size / 2.0 if y_line % 2 != 0 else 0.0
                    for x_line in range(self.grid_width): cell_x_line = x_line * self.cell_size + x_offset_line; cell_y_line = y_line * self.cell_size; painter.drawRect(QRectF(cell_x_line, cell_y_line, self.cell_size, self.cell_size))
        painter.restore() 
        if (self.mirror_mode_horizontal and self.grid_width > 1) or (self.mirror_mode_vertical and self.grid_height > 1):
            mirror_pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine); mirror_pen.setCosmetic(True); painter.setPen(mirror_pen)
            center_x_unscaled = (self.grid_width / 2.0 + (0.25 if self.grid_type == "Peyote/Brick" else 0.0)) * self.cell_size
            center_y_unscaled = (self.grid_height / 2.0) * self.cell_size
            transform = QTransform().translate(self.pan_offset.x(), self.pan_offset.y()).scale(self.zoom_factor, self.zoom_factor)
            center_screen = transform.map(QPointF(center_x_unscaled, center_y_unscaled))
            top_left_screen = transform.map(QPointF(0.0, 0.0))
            width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
            max_x_unscaled = width_multiplier * self.cell_size; max_y_unscaled = self.grid_height * self.cell_size
            bottom_right_screen = transform.map(QPointF(max_x_unscaled, max_y_unscaled))
            if self.mirror_mode_horizontal and self.grid_width > 1: painter.drawLine(QPointF(center_screen.x(), top_left_screen.y()), QPointF(center_screen.x(), bottom_right_screen.y()))
            if self.mirror_mode_vertical and self.grid_height > 1: painter.drawLine(QPointF(top_left_screen.x(), center_screen.y()), QPointF(bottom_right_screen.x(), center_screen.y())) 


    # --- Mouse/Coordinate Conversion (Unchanged) ---
    def _get_scene_pos(self, widget_pos: QPoint) -> QPointF: 
        # ... (código sin cambios)
        return (QPointF(widget_pos) - self.pan_offset) / self.zoom_factor
    def _get_widget_pos(self, scene_pos: QPointF) -> QPoint: 
        # ... (código sin cambios)
        return (scene_pos * self.zoom_factor + self.pan_offset).toPoint()
    def _get_cell_coords_from_pos(self, event_pos: QPoint) -> tuple[int, int] | None:
        # ... (código sin cambios)
        scene_pos = self._get_scene_pos(event_pos)
        y = int(scene_pos.y() // self.cell_size)
        x_offset = self.cell_size / 2.0 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0.0
        x = int((scene_pos.x() - x_offset) // self.cell_size)
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            if self.grid_type == "Peyote/Brick":
                 cell_start_x = x * self.cell_size + x_offset
                 if not (cell_start_x <= scene_pos.x() < cell_start_x + self.cell_size): return None 
            return x, y
        return None

    # --- _paint_cell and Command Logic (Unchanged) ---
    def _paint_cell(self, event_pos: QPoint):
        # ... (código sin cambios)
        coords = self._get_cell_coords_from_pos(event_pos)
        if coords is None: return 
        x, y = coords
        new_color = None if self.current_color.alpha() == 0 else self.current_color
        changes: dict[tuple[int, int], tuple[QColor | None, QColor | None]] = {}
        cells_to_process: set[tuple[int, int]] = {(x, y)} 
        mirrored_x = self.grid_width - 1 - x
        mirrored_y = self.grid_height - 1 - y
        if self.mirror_mode_horizontal and mirrored_x != x: cells_to_process.add((mirrored_x, y))
        if self.mirror_mode_vertical and mirrored_y != y: cells_to_process.add((x, mirrored_y))
        if self.mirror_mode_horizontal and self.mirror_mode_vertical and mirrored_x != x and mirrored_y != y: cells_to_process.add((mirrored_x, mirrored_y)) 
        for px, py in cells_to_process:
             if 0 <= px < self.grid_width and 0 <= py < self.grid_height: 
                 old_color = self.grid_data[py][px]
                 if old_color != new_color: changes[(px, py)] = (old_color, new_color)
        if changes: cmd = PaintCommand(self, changes); self._execute_command(cmd)

    def _execute_command(self, command: Command, merge: bool = False):
        # ... (código sin cambios)
        merged = False
        if merge and self.undo_stack:
             last_cmd = self.undo_stack[-1]
             if hasattr(last_cmd, 'merge_with') and callable(last_cmd.merge_with):
                  if last_cmd.merge_with(command):
                       merged = True
                       last_cmd.execute() 
        if not merged:
            command.execute()
            self.undo_stack.append(command)
            if self.redo_stack: self.redo_stack.clear()
        self._emit_undo_redo_state()

    # --- Undo/Redo Methods (Unchanged) ---
    def undo(self):
        # ... (código sin cambios)
        if self.undo_stack:
            command = self.undo_stack.pop(); command.undo(); self.redo_stack.append(command); self._emit_undo_redo_state()
    def redo(self):
        # ... (código sin cambios)
        if self.redo_stack:
            command = self.redo_stack.pop(); command.execute(); self.undo_stack.append(command); self._emit_undo_redo_state()
    def _emit_undo_redo_state(self):
        # ... (código sin cambios)
        can_undo = len(self.undo_stack) > 0; can_redo = len(self.redo_stack) > 0
        self.undo_redo_changed.emit(can_undo, can_redo)
    def _clear_history(self):
        # ... (código sin cambios)
        self.undo_stack.clear(); self.redo_stack.clear(); self._emit_undo_redo_state() 

    # --- Event Handlers (Unchanged) ---
    def wheelEvent(self, event: QWheelEvent):
        # ... (código sin cambios)
        mouse_point = event.position(); scene_point_before_zoom = self._get_scene_pos(mouse_point.toPoint()) 
        delta = event.angleDelta().y(); zoom_factor_delta = self.ZOOM_STEP if delta > 0 else 1.0 / self.ZOOM_STEP
        new_zoom_factor = self.zoom_factor * zoom_factor_delta
        clamped_zoom_factor = max(self.MIN_ZOOM, min(new_zoom_factor, self.MAX_ZOOM))
        if clamped_zoom_factor != self.zoom_factor:
            self.pan_offset = QPointF(mouse_point) - scene_point_before_zoom * clamped_zoom_factor
            self.zoom_factor = clamped_zoom_factor
            self._update_canvas_size_hint(); self.update() 
    def mousePressEvent(self, event: QMouseEvent):
        # ... (código sin cambios)
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging_paint = True; self._paint_cell(event.pos()) 
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.last_pan_pos = event.pos(); self.setCursor(Qt.CursorShape.ClosedHandCursor)
    def mouseMoveEvent(self, event: QMouseEvent):
        # ... (código sin cambios)
        if event.buttons() & Qt.MouseButton.LeftButton and self._is_dragging_paint:
            self._paint_cell(event.pos()) 
        elif event.buttons() & Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            delta = QPointF(event.pos() - self.last_pan_pos); self.pan_offset += delta; self.last_pan_pos = event.pos(); self.update() 
    def mouseReleaseEvent(self, event: QMouseEvent):
        # ... (código sin cambios)
        if event.button() == Qt.MouseButton.LeftButton: self._is_dragging_paint = False
        elif event.button() == Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            self.last_pan_pos = None; self.setCursor(Qt.CursorShape.ArrowCursor) 

    # --- Data Management (Unchanged) ---
    def clear_grid(self):
        # ... (código sin cambios)
        self.grid_data = self._create_grid(self.grid_width, self.grid_height); self._clear_history(); self.update() 
    def get_grid_data(self) -> list[list[str | None]]:
        # ... (código sin cambios)
        hex_grid = [];
        for row in self.grid_data: hex_row = [color.name() if color else None for color in row]; hex_grid.append(hex_row)
        return hex_grid
    def load_grid_data(self, hex_grid: list[list[str | None]]) -> bool:
        # ... (código sin cambios)
        try:
            self.zoom_factor = 1.0; self.pan_offset = QPointF(0.0, 0.0); self._clear_history() 
            new_height = len(hex_grid); new_width = 0 if new_height == 0 else (len(hex_grid[0]) if hex_grid[0] else 0) 
            new_grid_data = []
            for y in range(new_height):
                row_data = hex_grid[y]
                if not isinstance(row_data, list): new_grid_data.append([None] * new_width); continue 
                current_row_len = len(row_data); new_row = []
                for x in range(new_width):
                    if x < current_row_len:
                         hex_color = row_data[x]; q_color = None
                         if isinstance(hex_color, str) and hex_color.startswith('#'):
                              temp_color = QColor(hex_color)
                              if temp_color.isValid(): q_color = temp_color
                         new_row.append(q_color)
                    else: new_row.append(None) 
                new_grid_data.append(new_row)
            self.grid_data = new_grid_data; self.grid_width = new_width; self.grid_height = new_height
            self._update_canvas_size_hint(); self.update(); return True
        except Exception as e: print(f"Error loading grid data: {e}"); return False

# --- Fin de la clase GridCanvas ---