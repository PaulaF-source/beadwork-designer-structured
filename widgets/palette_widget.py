# widgets/palette_widget.py (v9.5 - Emite Índice para Edición)

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import (
    QPixmap, QColor, QPainter, QPen, QBrush, QMouseEvent, 
    QRadialGradient, QGradient
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QRectF, QPoint, 
    QPointF
)

try:
    from models import BeadColorEntry
except ImportError:
    print("FATAL: Cannot import BeadColorEntry from models.py. Check path.")
    class BeadColorEntry:
         def __init__(self, color, finish="Opaque", code=None, name=None): self.color = color; self.finish=finish; self.code=code; self.name=name
         def is_shiny(self): return False
         def __repr__(self): return str(self.color.name())


class PaletteWidget(QLabel):
    """
    Emite la entrada de metadata completa (BeadColorEntry) al seleccionar,
    y el índice (int) al hacer doble clic para editar/añadir.
    """
    # Emite la entrada completa al hacer clic (para pintar)
    colorSelected = pyqtSignal(BeadColorEntry) 
    
    # Emite el ÍNDICE (int) de la celda al hacer doble clic (para editar/añadir)
    colorRequest = pyqtSignal(int) 

    PRESET_COLORS = [
        ("#FFD700", "Metallic Gold", "Metallic"), 
        ("#C0C0C0", "Galvanized Silver", "Galvanized"), 
        ("#CD7F32", "Opaque Bronze", "Opaque"), 
        ("#1C1C1C", "Shiny Black Luster", "Luster"), 
        ("#FFFDD0", "Opaque Creamy White", "Opaque")
    ]
    ROWS = 3; COLS = 15; CELL_SIZE = 30; SPACING = 5
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.palette_set: set[str] = set() 
        self.colors: list[BeadColorEntry | None] = [None] * (self.ROWS * self.COLS) 
        self.tooltips: list[str | None] = [None] * (self.ROWS * self.COLS)
        self.preset_indices: set[int] = set() 
        self.next_open_slot: int = 0 
        self.hovered_index: int = -1 
        
        w = (self.CELL_SIZE * self.COLS) + (self.SPACING * (self.COLS + 1))
        h = (self.CELL_SIZE * self.ROWS) + (self.SPACING * (self.ROWS + 1))
        self.setFixedSize(w, h)
        
        self.setMouseTracking(True) 
        self.setup_default_palette() 
        self.draw_palette() 
        
    def setup_default_palette(self):
        """Initializes the palette with eraser and preset colors."""
        total_cells = self.ROWS * self.COLS
        self.colors = [None] * total_cells
        self.tooltips = ["Empty"] * total_cells
        self.palette_set.clear()
        self.preset_indices.clear() 
        
        eraser_color = QColor(0, 0, 0, 0) 
        eraser_entry = BeadColorEntry(eraser_color, finish="Eraser", name="Eraser")
        self.colors[0] = eraser_entry
        self.tooltips[0] = "Eraser (Clear cell)"
        self.preset_indices.add(0) # El borrador es un preset
        self.next_open_slot = 1 

        for hex_color, name, finish in self.PRESET_COLORS:
            if self.next_open_slot >= total_cells: break 
            color = QColor(hex_color)
            if color.isValid(): 
                entry = BeadColorEntry(color, finish=finish, name=name)
                
                self.colors[self.next_open_slot] = entry
                self.tooltips[self.next_open_slot] = f"{name} ({finish})" 
                self.palette_set.add(color.name()) 
                self.preset_indices.add(self.next_open_slot) # Añadir presets al conjunto
                self.next_open_slot += 1
            else: print(f"Warning: Preset color '{hex_color}' is invalid.")
            
        self.next_open_slot = min(self.next_open_slot, total_cells) 

    def add_color_entry(self, entry: BeadColorEntry):
        """Añade una entrada de color ya formada a la paleta, priorizando huecos."""
        color_name = entry.color.name()
        if not entry.color.isValid() or color_name in self.palette_set: 
             return 

        target_index = self._find_next_open_slot()
        if target_index == -1:
            print("Palette full. Cannot add more colors.")
            return

        self._set_entry_at_index(target_index, entry)
        
    def update_color_entry(self, index: int, entry: BeadColorEntry):
        """Actualiza una entrada existente en un índice específico (para Edición)."""
        if not (0 <= index < len(self.colors)):
            return
            
        # Eliminar el color antiguo del set de duplicados
        old_entry = self.colors[index]
        if old_entry and old_entry.color.name() in self.palette_set:
            self.palette_set.remove(old_entry.color.name())
            
        self._set_entry_at_index(index, entry)

    def _set_entry_at_index(self, index: int, entry: BeadColorEntry):
        """Función auxiliar interna para establecer la entrada y redibujar."""
        self.colors[index] = entry
        self.tooltips[index] = f"Color: {entry.name}\nFinish: {entry.finish}\nCode: {entry.code or 'N/A'}"
        self.palette_set.add(entry.color.name())
        self.draw_palette()

    def _find_next_open_slot(self) -> int:
        """Encuentra el primer índice 'None' después de los presets."""
        total_cells = self.ROWS * self.COLS
        start_search_index = len(self.preset_indices) # Asumiendo que los presets son contiguos al inicio

        for i in range(start_search_index, total_cells):
            if self.colors[i] is None:
                return i
        
        # Si no hay huecos, revisar si next_open_slot sigue siendo válido
        if self.next_open_slot < total_cells:
             # Validar que next_open_slot no esté en los presets (aunque no debería)
             if self.colors[self.next_open_slot] is None:
                 idx = self.next_open_slot
                 self.next_open_slot += 1
                 return idx
        
        return -1 # Indica que la paleta está llena

    def add_color(self, color: QColor):
        """(Compatibilidad con Image Picker) Añade un color básico."""
        if not color.isValid() or color.name() in self.palette_set: return 
        
        new_entry = BeadColorEntry(color, finish="Opaque (Image Pick)", name=color.name().upper())
        self.add_color_entry(new_entry) 
        
    def draw_palette(self):
        pixmap = QPixmap(self.size()); pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for r in range(self.ROWS):
            for c in range(self.COLS):
                index = (r * self.COLS) + c
                entry = self.colors[index] 
                
                x = self.SPACING + (c * (self.CELL_SIZE + self.SPACING))
                y = self.SPACING + (r * (self.CELL_SIZE + self.SPACING))
                rect = QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)
                is_hovered = (index == self.hovered_index)
                
                if index == 0: # Eraser
                    pen = QPen(QColor("#f8d7da"), 1, Qt.PenStyle.DashLine); brush = QBrush(QColor("#4f2222"))
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2)
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                    eraser_pen = QPen(QColor("#f8d7da"), 2); painter.setPen(eraser_pen); painter.setBrush(Qt.BrushStyle.NoBrush)
                    margin = 7; painter.drawLine(int(rect.left()+margin), int(rect.top()+margin), int(rect.right()-margin), int(rect.bottom()-margin)); painter.drawLine(int(rect.left()+margin), int(rect.bottom()-margin), int(rect.right()-margin), int(rect.top()+margin))
                
                elif entry is None: # Empty
                    pen = QPen(QColor("#777"), 1, Qt.PenStyle.DashLine); brush = QBrush(QColor("#404040"))
                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine) 
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                
                else: # Color
                    color = entry.color
                    pen = QPen(QColor("#1a1a1a"), 1); brush = QBrush(color)
                    
                    if entry.is_shiny():
                        grad = QRadialGradient(rect.topLeft(), rect.width())
                        grad.setCenter(rect.topLeft() + QPointF(rect.width() * 0.25, rect.height() * 0.25))
                        grad.setFocalPoint(rect.topLeft() + QPointF(rect.width() * 0.1, rect.height() * 0.1))
                        grad.setColorAt(0.0, color.lighter(150)) 
                        grad.setColorAt(0.7, color)
                        grad.setColorAt(1.0, color.darker(110)) 
                        brush = QBrush(grad)
                        pen = QPen(QColor("#f0f0f0"), 1) 

                    if is_hovered: pen = QPen(Qt.GlobalColor.white, 2) 
                    
                    painter.setPen(pen); painter.setBrush(brush); painter.drawRoundedRect(rect, 4, 4)
                    
        painter.end(); self.setPixmap(pixmap)

    def _get_index_from_pos(self, pos: QPoint) -> int:
        x, y = pos.x(), pos.y();
        if not (self.SPACING <= x < self.width() - self.SPACING and self.SPACING <= y < self.height() - self.SPACING): return -1
        col_float = (x - self.SPACING) / (self.CELL_SIZE + self.SPACING); row_float = (y - self.SPACING) / (self.CELL_SIZE + self.SPACING)
        if col_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING) or row_float % 1 > self.CELL_SIZE / (self.CELL_SIZE + self.SPACING): return -1
        c = int(col_float); r = int(row_float)
        if 0 <= r < self.ROWS and 0 <= c < self.COLS: return (r * self.COLS) + c
        return -1

    def mousePressEvent(self, event: QMouseEvent):
        index = self._get_index_from_pos(event.position())
        if index == -1: 
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            entry = self.colors[index]
            if entry is not None:
                self.colorSelected.emit(entry) 
                
        elif event.button() == Qt.MouseButton.RightButton:
            if index not in self.preset_indices and self.colors[index] is not None:
                entry_to_delete = self.colors[index]
                if entry_to_delete: 
                    color_name = entry_to_delete.color.name() 
                    if color_name in self.palette_set:
                         self.palette_set.remove(color_name) 
                         
                self.colors[index] = None 
                self.tooltips[index] = "Empty" 
                
                # No necesitamos ajustar next_open_slot aquí, _find_next_open_slot lo manejará.
                
                self.draw_palette() 
                if self.hovered_index == index:
                     self.hovered_index = -1 
                     self.setCursor(Qt.CursorShape.ArrowCursor) 
                     self.setToolTip("")
        super().mousePressEvent(event) 

    # --- MODIFICADO: Emite el índice (int) ---
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Emite el índice de la celda para edición (si no es un preset)."""
        index = self._get_index_from_pos(event.position())
        
        if index == -1 or event.button() != Qt.MouseButton.LeftButton:
            super().mouseDoubleClickEvent(event)
            return
        
        # No permitir editar el Borrador (0) ni los Presets
        if index in self.preset_indices:
            print(f"Edit locked for preset index: {index}")
            return 
        
        # Emitir el índice de la celda (ya sea vacía o llena)
        self.colorRequest.emit(index)

    def mouseMoveEvent(self, event: QMouseEvent):
        index = self._get_index_from_pos(event.position());
        if index != self.hovered_index: self.hovered_index = index; self.draw_palette()
        tooltip_to_show = ""; cursor_to_show = Qt.CursorShape.ArrowCursor
        
        if index != -1:
            entry = self.colors[index]
            if entry is not None:
                tooltip_to_show = f"Color: {entry.name}\nFinish: {entry.finish}\nCode: {entry.code or 'N/A'}"
                cursor_to_show = Qt.CursorShape.PointingHandCursor
            else:
                 tooltip_to_show = "Empty (Double-click to add)"
                 
        self.setToolTip(tooltip_to_show); self.setCursor(cursor_to_show); super().mouseMoveEvent(event)

    def leaveEvent(self, event): 
        if self.hovered_index != -1: self.hovered_index = -1; self.draw_palette(); self.setToolTip(""); self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def get_palette_data_with_metadata(self) -> list[dict]:
        """Retorna una lista de diccionarios para la persistencia JSON."""
        added_entries = []
        for i in range(len(self.colors)): 
             entry = self.colors[i]
             if entry and entry.color.isValid() and i not in self.preset_indices: 
                 added_entries.append({
                     "hex": entry.color.name(), 
                     "finish": entry.finish,
                     "code": entry.code,
                     "name": entry.name
                 })
        return added_entries

    def load_palette_entries(self, palette_data: list[dict]):
        """Carga colores desde una lista de diccionarios (incluyendo metadata)."""
        self.setup_default_palette() 
        
        for entry_data in palette_data:
            if not entry_data or not isinstance(entry_data, dict):
                 continue 

            hex_color = entry_data.get("hex")
            finish = entry_data.get("finish", "Opaque")
            code = entry_data.get("code")
            name = entry_data.get("name")
            
            color = QColor(hex_color)
            if color.isValid():
                new_entry = BeadColorEntry(color, finish=finish, code=code, name=name)
                self.add_color_entry(new_entry) 
                
        self.draw_palette()