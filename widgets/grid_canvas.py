# widgets/grid_canvas.py (v9.4 - Corrección de Fusión de Comandos)

from PyQt6.QtWidgets import QWidget, QSizePolicy, QRubberBand 
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QMouseEvent, QWheelEvent, QTransform,
    QRadialGradient
) 
from PyQt6.QtCore import (
    Qt, QPointF, QPoint, QRectF, pyqtSignal, QRect, QSize 
)

# --- Import Command classes ---
from commands import Command, PaintCommand, SelectionCommand

# --- Importar BeadColorEntry desde models.py ---
try:
    from models import BeadColorEntry
except ImportError:
    print("FATAL: Cannot import BeadColorEntry in GridCanvas.")
    class BeadColorEntry:
        def __init__(self, color, finish="Opaque", code=None, name=None): self.color = color; self.finish=finish; self.code=code; self.name=name
        def is_shiny(self): return False
        def __repr__(self): return str(self.color.name())
    
# --- Constante para el borrador ---
ERASER_ENTRY = BeadColorEntry(QColor(0, 0, 0, 0), finish="Eraser", name="Eraser")


class GridCanvas(QWidget):
    undo_redo_changed = pyqtSignal(bool, bool) 
    selection_changed = pyqtSignal(bool, bool) 

    MIN_ZOOM = 0.1; MAX_ZOOM = 5.0; ZOOM_STEP = 1.2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_width: int = 30 
        self.grid_height: int = 10
        self.cell_size: int = 12
        self.grid_type: str = "Square"
        
        self.grid_data: list[list[BeadColorEntry | None]] = self._create_grid(self.grid_width, self.grid_height)
        
        self.current_tool: str = "pencil" 
        self.current_entry: BeadColorEntry = ERASER_ENTRY 
        self.mirror_mode_horizontal: bool = False
        self.mirror_mode_vertical: bool = False
        
        self.zoom_factor: float = 1.0
        self.pan_offset: QPointF = QPointF(0.0, 0.0) 
        self.last_pan_pos: QPoint | None = None 
        
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self._is_dragging_paint = False 
        
        self.selection_rect: QRect | None = None 
        self.selection_origin: QPoint | None = None 
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        self.clipboard_data: list[list[BeadColorEntry | None]] | None = None 
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._update_canvas_size_hint()

    # --- Setters para Propiedades del Canvas ---
    
    def set_grid_type(self, grid_type: str):
        if self.grid_type != grid_type:
            self.grid_type = grid_type
            self._update_canvas_size_hint()
            self.update()

    def set_cell_size(self, cell_size: int):
        if self.cell_size != cell_size:
            self.cell_size = cell_size
            self._update_canvas_size_hint()
            self.update()

    def set_grid_size(self, w: int, h: int):
        if self.grid_width != w or self.grid_height != h:
            self.grid_width = w
            self.grid_height = h
            self.grid_data = self._create_grid(w, h) 
            self._clear_history()
            self.clear_selection()
            self._update_canvas_size_hint()
            self.update()

    # --- Setters de Entrada de Color ---
    def set_current_color(self, color: QColor): 
        pass

    def set_current_entry(self, entry: BeadColorEntry):
        self.current_entry = entry
        self.set_current_color(entry.color) 

    def set_current_tool(self, tool: str):
        if self.current_tool == "select" and tool != "select":
            self.clear_selection() 
        self.current_tool = tool
        if tool == "select": self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool == "pencil": self.setCursor(Qt.CursorShape.ArrowCursor) 
        elif tool == "fill": self.setCursor(Qt.CursorShape.PointingHandCursor) 
        else: self.setCursor(Qt.CursorShape.ArrowCursor) 
    
    # --- Métodos de Lógica Interna ---
    def _create_grid(self, w: int, h: int) -> list[list[BeadColorEntry | None]]: 
        return [[None for _ in range(w)] for _ in range(h)]
    
    def _update_canvas_size_hint(self):
        base_width_multiplier = self.grid_width + 0.5 if self.grid_type == "Peyote/Brick" else self.grid_width
        zoomed_width = int(base_width_multiplier * self.cell_size * self.zoom_factor) + 1 
        zoomed_height = int(self.grid_height * self.cell_size * self.zoom_factor) + 1
        self.setMinimumSize(zoomed_width, zoomed_height); self.updateGeometry() 

    # --- HISTORIAL DE COMANDOS (Undo/Redo) ---
    
    def _clear_history(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.undo_redo_changed.emit(False, False)

    # --- CORRECCIÓN CRÍTICA v9.4 ---
    def _execute_command(self, command: Command, merge: bool):
        """Ejecuta un comando, lo añade a la pila de deshacer y limpia la pila de rehacer."""
        
        if merge and self.undo_stack and self.undo_stack[-1].merge_with(command):
            # BUG FIX:
            # El comando se fusionó con el anterior (self.undo_stack[-1]).
            # Ahora, debemos RE-EJECUTAR el comando *fusionado* (el que está en el stack)
            # para aplicar los cambios *nuevos* al lienzo.
            self.undo_stack[-1].execute() # <-- Esta línea aplica el cambio fusionado
            
            self.undo_redo_changed.emit(True, False)
            # self.update() es llamado por .execute()
            return
        
        # Flujo normal (sin fusionar)
        command.execute()
        self.undo_stack.append(command)
        
        self.redo_stack.clear()
        self.undo_redo_changed.emit(bool(self.undo_stack), bool(self.redo_stack))
        
        
    def undo(self):
        """Deshace la última acción."""
        if not self.undo_stack:
            return
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        self.undo_redo_changed.emit(bool(self.undo_stack), bool(self.redo_stack))

    def redo(self):
        """Rehace la acción deshecha."""
        if not self.redo_stack:
            return
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        self.undo_redo_changed.emit(bool(self.undo_stack), bool(self.redo_stack))

    # --- Pintura (Implementación del brillo) ---
    def paintEvent(self, event): 
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) 
        painter.fillRect(self.rect(), QColor("#e0e0e0")) 
        painter.save(); painter.translate(self.pan_offset); painter.scale(self.zoom_factor, self.zoom_factor) 
        
        for y in range(self.grid_height):
            x_offset = self.cell_size / 2 if self.grid_type == "Peyote/Brick" and y % 2 != 0 else 0
            for x in range(self.grid_width):
                entry = self.grid_data[y][x]
                
                if entry: 
                    cell_rect = QRectF(x * self.cell_size + x_offset, y * self.cell_size, self.cell_size, self.cell_size)
                    color = entry.color
                    
                    if entry.is_shiny():
                        grad = QRadialGradient(cell_rect.topLeft(), cell_rect.width())
                        grad.setCenter(cell_rect.topLeft() + QPointF(cell_rect.width() * 0.3, cell_rect.height() * 0.3))
                        grad.setFocalPoint(cell_rect.topLeft() + QPointF(cell_rect.width() * 0.1, cell_rect.height() * 0.1))
                        grad.setColorAt(0.0, color.lighter(150)) 
                        grad.setColorAt(0.7, color)
                        grad.setColorAt(1.0, color.darker(110)) 
                        brush = QBrush(grad)
                        
                        painter.setBrush(brush)
                        painter.setPen(Qt.PenStyle.NoPen) 
                        painter.drawRect(cell_rect)
                        
                    else:
                        painter.fillRect(cell_rect, QBrush(color))
                        
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
        
        if self.selection_rect:
            selection_pen = QPen(QColor("#007bff"), 2); selection_pen.setCosmetic(True); selection_pen.setStyle(Qt.PenStyle.DashLine); painter.setPen(selection_pen); painter.setBrush(Qt.BrushStyle.NoBrush) 
            rect_f = QRectF(self.selection_rect.x() * self.cell_size, self.selection_rect.y() * self.cell_size, self.selection_rect.width() * self.cell_size, self.selection_rect.height() * self.cell_size)
            painter.drawRect(rect_f)
        
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


    # --- Paint/Fill Logic ---
    def _paint_cell(self, event_pos: QPoint):
        coords = self._get_cell_coords_from_pos(event_pos);
        if coords is None: return 
        
        x, y = coords
        new_entry = None if self.current_entry.finish == "Eraser" else self.current_entry 
        
        if new_entry is not None and not isinstance(new_entry, BeadColorEntry):
             print("Error: current_entry no es una BeadColorEntry válida.")
             return
             
        changes: dict[tuple[int, int], tuple[BeadColorEntry | None, BeadColorEntry | None]] = {}
        cells_to_process: set[tuple[int, int]] = {(x, y)} 
        mirrored_x = self.grid_width - 1 - x; mirrored_y = self.grid_height - 1 - y
        
        if self.mirror_mode_horizontal and mirrored_x != x: cells_to_process.add((mirrored_x, y))
        if self.mirror_mode_vertical and mirrored_y != y: cells_to_process.add((x, mirrored_y))
        if self.mirror_mode_horizontal and self.mirror_mode_vertical and mirrored_x != x and mirrored_y != y: cells_to_process.add((mirrored_x, mirrored_y)) 
        
        for px, py in cells_to_process:
             if 0 <= px < self.grid_width and 0 <= py < self.grid_height: 
                 old_entry = self.grid_data[py][px]
                 if old_entry != new_entry: 
                     changes[(px, py)] = (old_entry, new_entry)
                     
        if changes: 
             cmd = PaintCommand(self, changes) 
             self._execute_command(cmd, merge=self._is_dragging_paint)
             
    def _flood_fill(self, event_pos: QPoint):
        coords = self._get_cell_coords_from_pos(event_pos);
        if coords is None: return
        
        x, y = coords
        new_entry = None if self.current_entry.finish == "Eraser" else self.current_entry
        target_entry = self.grid_data[y][x]
        
        if target_entry == new_entry: return
        
        changes: dict[tuple[int, int], tuple[BeadColorEntry | None, BeadColorEntry | None]] = {}
        queue: list[tuple[int, int]] = [(x, y)]; processed: set[tuple[int, int]] = {(x, y)}
        changes[(x, y)] = (target_entry, new_entry)
        
        while queue:
            cx, cy = queue.pop(0)
            for nx, ny in [(cx, cy - 1), (cx, cy + 1), (cx - 1, cy), (cx + 1, cy)]:
                if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and (nx, ny) not in processed):
                    processed.add((nx, ny)); 
                    neighbor_entry = self.grid_data[ny][nx]
                    if neighbor_entry == target_entry: 
                        changes[(nx, ny)] = (target_entry, new_entry)
                        queue.append((nx, ny))
                        
        if changes: 
            cmd = PaintCommand(self, changes)
            self._execute_command(cmd, merge=False)


    # --- Data Management ---
    
    def clear_grid(self):
        self.grid_data = self._create_grid(self.grid_width, self.grid_height); self._clear_history(); self.clear_selection(); self.update() 
    
    def get_grid_data(self) -> list[list[str | None]]:
        """Retorna la cuadrícula como códigos HEX o None para guardar."""
        hex_grid = [];
        for row in self.grid_data: 
             hex_row = [entry.color.name() if entry else None for entry in row]
             hex_grid.append(hex_row)
        return hex_grid

    def load_grid_data(self, hex_grid: list[list[str | None]]) -> bool:
        """
        Carga la cuadrícula desde códigos HEX. Los datos cargados se marcan 
        temporalmente como Opaco hasta que se complete la carga de la paleta.
        """
        try:
            self.zoom_factor = 1.0; self.pan_offset = QPointF(0.0, 0.0); self._clear_history(); self.clear_selection()
            new_height = len(hex_grid); new_width = 0 if new_height == 0 else (len(hex_grid[0]) if hex_grid[0] else 0) 
            new_grid_data = []
            
            for y in range(new_height):
                row_data = hex_grid[y]
                if not isinstance(row_data, list): new_grid_data.append([None] * new_width); continue 
                current_row_len = len(row_data); new_row = []
                for x in range(new_width):
                    entry = None
                    if x < current_row_len:
                         hex_color = row_data[x]
                         if isinstance(hex_color, str) and hex_color.startswith('#'):
                              temp_color = QColor(hex_color)
                              if temp_color.isValid(): 
                                  entry = BeadColorEntry(temp_color, finish="Opaque (Loaded)", name=temp_color.name().upper())
                         
                    new_row.append(entry) 
                new_grid_data.append(new_row)
                
            self.grid_data = new_grid_data; self.grid_width = new_width; self.grid_height = new_height
            self._update_canvas_size_hint(); self.update(); return True
            
        except Exception as e: print(f"Error loading grid data: {e}"); return False

    # --- MÉTODOS DE INTERACCIÓN (Restaurados) ---
    def _get_scene_pos(self, widget_pos: QPoint) -> QPointF: return (QPointF(widget_pos) - self.pan_offset) / self.zoom_factor
    def _get_cell_coords_from_pos(self, event_pos: QPoint) -> tuple[int, int] | None:
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

    def wheelEvent(self, event: QWheelEvent):
        mouse_point = event.position(); scene_point_before_zoom = self._get_scene_pos(mouse_point.toPoint()) 
        delta = event.angleDelta().y(); zoom_factor_delta = self.ZOOM_STEP if delta > 0 else 1.0 / self.ZOOM_STEP
        new_zoom_factor = self.zoom_factor * zoom_factor_delta
        clamped_zoom_factor = max(self.MIN_ZOOM, min(new_zoom_factor, self.MAX_ZOOM))
        if clamped_zoom_factor != self.zoom_factor:
            self.pan_offset = QPointF(mouse_point) - scene_point_before_zoom * clamped_zoom_factor
            self.zoom_factor = clamped_zoom_factor
            self._update_canvas_size_hint(); self.update() 
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_tool == "pencil":
                self._is_dragging_paint = True; self._paint_cell(event.pos()) 
            elif self.current_tool == "fill":
                 self._is_dragging_paint = False; self._flood_fill(event.pos())
            elif self.current_tool == "select":
                self.clear_selection(); self.selection_origin = event.pos()
                self.rubber_band.setGeometry(QRect(self.selection_origin, QSize())) 
                self.rubber_band.show()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.last_pan_pos = event.pos(); self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.current_tool == "pencil" and self._is_dragging_paint: self._paint_cell(event.pos()) 
            elif self.current_tool == "select" and self.selection_origin is not None:
                self.rubber_band.setGeometry(QRect(self.selection_origin, event.pos()).normalized())
        elif event.buttons() & Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            delta = QPointF(event.pos() - self.last_pan_pos); self.pan_offset += delta; self.last_pan_pos = event.pos(); self.update() 
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
             self._is_dragging_paint = False 
             if self.current_tool == "select" and self.selection_origin is not None:
                self.rubber_band.hide()
                widget_rect = self.rubber_band.geometry()
                top_left_coords = self._get_cell_coords_from_pos(widget_rect.topLeft())
                bottom_right_coords = self._get_cell_coords_from_pos(widget_rect.bottomRight())
                if top_left_coords and bottom_right_coords:
                    self.selection_rect = QRect(
                        top_left_coords[0], top_left_coords[1],
                        bottom_right_coords[0] - top_left_coords[0] + 1, 
                        bottom_right_coords[1] - top_left_coords[1] + 1  
                    ).normalized()
                    self.selection_changed.emit(True, self.clipboard_data is not None) 
                else:
                    self.selection_rect = None
                    self.selection_changed.emit(False, self.clipboard_data is not None) 
                self.selection_origin = None
                self.update() 
        elif event.button() == Qt.MouseButton.MiddleButton and self.last_pan_pos is not None:
            self.last_pan_pos = None; self.setCursor(Qt.CursorShape.ArrowCursor) 

    def clear_selection(self):
        if self.selection_rect is not None:
            self.selection_rect = None
            self.selection_changed.emit(False, self.clipboard_data is not None) 
            self.update() 

    def _get_data_from_selection(self) -> list[list[BeadColorEntry | None]] | None:
        if not self.selection_rect:
            return None
        data = []
        for r in range(self.selection_rect.height()):
            row = []
            y = self.selection_rect.y() + r
            if 0 <= y < self.grid_height:
                for c in range(self.selection_rect.width()):
                    x = self.selection_rect.x() + c
                    if 0 <= x < self.grid_width:
                        row.append(self.grid_data[y][x])
                    else:
                        row.append(None) 
            else:
                row = [None] * self.selection_rect.width() 
            data.append(row)
        return data

    def copy_selection(self):
        if not self.selection_rect: return
        self.clipboard_data = self._get_data_from_selection()
        self.selection_changed.emit(True, True) 

    def cut_selection(self):
        if not self.selection_rect: return
        self.copy_selection() 
        cmd = SelectionCommand(self, self.selection_rect, paste_data=None) 
        self._execute_command(cmd, merge=False)

    def paste_selection(self):
        if not self.clipboard_data or not self.selection_rect: return
        paste_width = len(self.clipboard_data[0]) if self.clipboard_data else 0
        paste_height = len(self.clipboard_data)
        if paste_width == 0 or paste_height == 0: return
        target_rect = QRect(self.selection_rect.topLeft(), QSize(paste_width, paste_height))
        cmd = SelectionCommand(self, target_rect, paste_data=self.clipboard_data)
        self._execute_command(cmd, merge=False)

    def delete_selection(self):
        if not self.selection_rect: return
        cmd = SelectionCommand(self, self.selection_rect, paste_data=None) 
        self._execute_command(cmd, merge=False)
        self.clear_selection()