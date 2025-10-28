# main_window.py (v8.3 - Iconos de simetría mejorados, cambio de color en activo)

import sys 
import json

# --- Qt Modules ---
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QFrame, QSizePolicy, QComboBox,
    QScrollArea, QApplication, QDialog, 
    QButtonGroup 
)
from PyQt6.QtGui import (
    QIcon, QColor, QImage, QAction, QKeySequence, QPixmap, QPainter
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QPointF

# --- Import Widgets ---
from widgets.image_picker import ImageColorPicker
from widgets.palette_widget import PaletteWidget
from widgets.grid_canvas import GridCanvas 
from widgets.crop_dialog import CropDialog
from widgets.preview_dialog import PreviewDialog

# --- Import Utilities ---
from utils.helpers import (
    svg_to_qicon, 
    ICON_SAVE, ICON_LOAD, ICON_EXPORT, ICON_CLEAR, ICON_PREVIEW, 
    ICON_UNDO, ICON_REDO,
    ICON_PENCIL, 
    # --- MODIFICADO: Usar los nuevos iconos descriptivos ---
    ICON_SYMMETRY_VERTICAL_DESCRIPTIVE, ICON_SYMMETRY_HORIZONTAL_DESCRIPTIVE
)
from utils.constants import PRESET_SIZES, DEFAULT_PRESET_NAME

# --- Constantes de Color (Para iconos activos/inactivos) ---
ICON_COLOR_INACTIVE = "#f8f9fa"  # Blanco/claro (por defecto)
ICON_COLOR_ACTIVE = "#28a745"    # Verde, para indicar que está activo

# --- MainWindow class definition ---
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.version = "8.3" # Versión actualizada
        self.setWindowTitle(f"Beadwork Designer v{self.version}") 
        self.image_load_index = 0 
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Panel (Sin cambios) ---
        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(570); left_panel.setObjectName("LeftPanel")
        left_layout.setContentsMargins(0, 0, 0, 0); left_layout.setSpacing(0)
        inspiration_frame = QFrame(); inspiration_frame.setObjectName("SectionFrame")
        inspiration_layout = QVBoxLayout(inspiration_frame); inspiration_layout.setContentsMargins(10, 10, 10, 10)
        load_section_label = QLabel("Inspiration"); load_section_label.setObjectName("SectionHeader"); inspiration_layout.addWidget(load_section_label)
        self.btn_load_image = QPushButton(); self.btn_load_image.setIcon(svg_to_qicon(ICON_LOAD)); self.btn_load_image.setIconSize(QSize(24, 24)); self.btn_load_image.setToolTip("Load Inspiration Image"); self.btn_load_image.setObjectName("PrimaryButton"); inspiration_layout.addWidget(self.btn_load_image)
        image_grid_container = QWidget(); image_grid = QGridLayout(image_grid_container); image_grid_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.image_pickers = [ImageColorPicker() for _ in range(4)] 
        image_grid.addWidget(self.image_pickers[0], 0, 0); image_grid.addWidget(self.image_pickers[1], 0, 1); image_grid.addWidget(self.image_pickers[2], 1, 0); image_grid.addWidget(self.image_pickers[3], 1, 1)
        image_grid.setHorizontalSpacing(10); image_grid.setVerticalSpacing(10); image_grid.setContentsMargins(0, 5, 0, 0)
        image_grid.setColumnStretch(0, 1); image_grid.setColumnStretch(1, 1); image_grid.setRowStretch(0, 1); image_grid.setRowStretch(1, 1)
        inspiration_layout.addWidget(image_grid_container)
        palette_section_frame = QFrame(); palette_section_frame.setObjectName("SectionFrame")
        palette_section_layout = QVBoxLayout(palette_section_frame); palette_section_layout.setContentsMargins(10, 10, 10, 10)
        palette_label = QLabel("Color Palette"); palette_label.setObjectName("SectionHeader")
        self.palette_widget = PaletteWidget() 
        self.current_color_label = QLabel("Selected:"); self.current_color_swatch = QLabel(); self.current_color_swatch.setFixedSize(30, 30); self.current_color_swatch.setStyleSheet("border: 1px solid #555; background-color: #2c2c2c;") 
        current_color_layout = QHBoxLayout(); current_color_layout.addWidget(self.current_color_label); current_color_layout.addWidget(self.current_color_swatch); current_color_layout.addStretch()
        palette_section_layout.addWidget(palette_label); palette_section_layout.addWidget(self.palette_widget); palette_section_layout.addLayout(current_color_layout)
        left_layout.addWidget(inspiration_frame); left_layout.addWidget(palette_section_frame); left_layout.addStretch() 

        # --- Right Panel (Sin cambios mayores) ---
        right_panel = QWidget(); right_panel.setObjectName("RightPanel"); right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0); right_layout.setSpacing(0)

        # --- Section 3: Design Canvas ---
        design_section_frame = QFrame(); design_section_frame.setObjectName("SectionFrame"); design_section_layout = QVBoxLayout(design_section_frame); design_section_layout.setContentsMargins(10, 10, 10, 10)
        
        # Cabecera de "Design Canvas"
        design_header_layout = QHBoxLayout()
        design_label = QLabel("Design Canvas"); design_label.setObjectName("SectionHeader")
        design_header_layout.addWidget(design_label)
        design_header_layout.addStretch() 
        design_section_layout.addLayout(design_header_layout)

        # --- Barra de herramientas de pintado ---
        tool_toolbar_layout = QHBoxLayout()
        tool_toolbar_layout.setContentsMargins(0, 0, 0, 5) 
        
        # Grupo de botones para Herramientas (Lápiz, Bote de pintura, etc.)
        self.paint_tool_group = QButtonGroup(self)
        self.paint_tool_group.setExclusive(True)

        # Botón Lápiz (Herramienta)
        self.btn_tool_pencil = QPushButton()
        self.btn_tool_pencil.setIcon(svg_to_qicon(ICON_PENCIL, ICON_COLOR_INACTIVE)) # Color inicial
        self.btn_tool_pencil.setToolTip("Pencil Tool (Default)")
        self.btn_tool_pencil.setCheckable(True)
        self.btn_tool_pencil.setChecked(True) # Empezar con este seleccionado
        self.paint_tool_group.addButton(self.btn_tool_pencil, 0) # ID 0
        tool_toolbar_layout.addWidget(self.btn_tool_pencil)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        tool_toolbar_layout.addWidget(separator)

        # Botón Simetría Vertical (Modo)
        self.btn_tool_sym_v = QPushButton()
        # MODIFICADO: Usar el nuevo icono descriptivo y aplicar color inicial
        self.btn_tool_sym_v.setIcon(svg_to_qicon(ICON_SYMMETRY_VERTICAL_DESCRIPTIVE, ICON_COLOR_INACTIVE)) 
        self.btn_tool_sym_v.setToolTip("Toggle Vertical Symmetry (Mirrors drawing horizontally)") # Tooltip mejorado
        self.btn_tool_sym_v.setCheckable(True) 
        tool_toolbar_layout.addWidget(self.btn_tool_sym_v)

        # Botón Simetría Horizontal (Modo)
        self.btn_tool_sym_h = QPushButton()
        # MODIFICADO: Usar el nuevo icono descriptivo y aplicar color inicial
        self.btn_tool_sym_h.setIcon(svg_to_qicon(ICON_SYMMETRY_HORIZONTAL_DESCRIPTIVE, ICON_COLOR_INACTIVE))
        self.btn_tool_sym_h.setToolTip("Toggle Horizontal Symmetry (Mirrors drawing vertically)") # Tooltip mejorado
        self.btn_tool_sym_h.setCheckable(True) 
        tool_toolbar_layout.addWidget(self.btn_tool_sym_h)

        tool_toolbar_layout.addStretch() 
        design_section_layout.addLayout(tool_toolbar_layout)

        self.canvas_scroll_area = QScrollArea(); self.canvas_scroll_area.setWidgetResizable(True); self.canvas_scroll_area.setObjectName("CanvasScrollArea"); self.canvas_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.grid_canvas = GridCanvas() 
        default_w, default_h = PRESET_SIZES[DEFAULT_PRESET_NAME]; initial_grid_type = "Square"; initial_cell_size = 12 
        self.grid_canvas.set_grid_type(initial_grid_type); self.grid_canvas.set_cell_size(initial_cell_size); self.grid_canvas.set_grid_size(default_w, default_h) 
        self.canvas_scroll_area.setWidget(self.grid_canvas)

        # --- IO Controls (Texto eliminado de Undo/Redo) ---
        io_controls_layout = QHBoxLayout()
        
        self.btn_undo = QPushButton(); self.btn_undo.setIcon(svg_to_qicon(ICON_UNDO)); self.btn_undo.setToolTip("Undo last action (Ctrl+Z)"); self.btn_undo.setEnabled(False) 
        self.btn_redo = QPushButton(); self.btn_redo.setIcon(svg_to_qicon(ICON_REDO)); self.btn_redo.setToolTip("Redo last undone action (Ctrl+Y)"); self.btn_redo.setEnabled(False) 
        
        self.btn_preview = QPushButton(); self.btn_preview.setIcon(svg_to_qicon(ICON_PREVIEW)); self.btn_preview.setToolTip("Preview Design")
        self.btn_save = QPushButton(); self.btn_save.setIcon(svg_to_qicon(ICON_SAVE)); self.btn_save.setToolTip("Save Design")
        self.btn_load = QPushButton(); self.btn_load.setIcon(svg_to_qicon(ICON_LOAD)); self.btn_load.setToolTip("Load Design")
        self.btn_export_png = QPushButton(); self.btn_export_png.setIcon(svg_to_qicon(ICON_EXPORT)); self.btn_export_png.setToolTip("Export as PNG")
        self.btn_clear_grid = QPushButton(); self.btn_clear_grid.setIcon(svg_to_qicon(ICON_CLEAR, color="#f8d7da")); self.btn_clear_grid.setObjectName("DangerButton"); self.btn_clear_grid.setToolTip("Clear Grid")
        
        io_controls_layout.addWidget(self.btn_undo); io_controls_layout.addWidget(self.btn_redo) 
        io_controls_layout.addSpacing(20); io_controls_layout.addWidget(self.btn_preview); io_controls_layout.addWidget(self.btn_save)
        io_controls_layout.addWidget(self.btn_load); io_controls_layout.addWidget(self.btn_export_png); io_controls_layout.addStretch() 
        io_controls_layout.addWidget(self.btn_clear_grid)
        design_section_layout.addWidget(self.canvas_scroll_area, 1); design_section_layout.addLayout(io_controls_layout)

        # --- Section 4: Define Size (Sin cambios) ---
        size_section_frame = QFrame(); size_section_frame.setObjectName("SectionFrame"); size_section_layout = QVBoxLayout(size_section_frame); size_section_layout.setContentsMargins(10, 10, 10, 10)
        size_label = QLabel("Canvas Size & Resolution"); size_label.setObjectName("SectionHeader")
        size_controls_layout = QGridLayout(); size_controls_layout.setHorizontalSpacing(15) 
        size_controls_layout.addWidget(QLabel("Presets:"), 0, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Custom Grid Size:"), 0, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Grid Type:"), 0, 2, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight) 
        size_controls_layout.addWidget(QLabel("Cell Size (px):"), 0, 3, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.combo_presets = QComboBox(); self.combo_presets.addItems(PRESET_SIZES.keys()); self.combo_presets.setCurrentText(DEFAULT_PRESET_NAME)
        size_controls_layout.addWidget(self.combo_presets, 1, 0, alignment=Qt.AlignmentFlag.AlignVCenter) 
        custom_size_sublayout = QHBoxLayout(); custom_size_sublayout.setContentsMargins(0, 0, 0, 0); custom_size_sublayout.setSpacing(5) 
        custom_size_sublayout.addWidget(QLabel("Cols:")); self.spin_grid_width = QSpinBox(); self.spin_grid_width.setRange(5, 500); self.spin_grid_width.setValue(default_w)
        custom_size_sublayout.addWidget(self.spin_grid_width); custom_size_sublayout.addSpacing(15); custom_size_sublayout.addWidget(QLabel("Rows:"))
        self.spin_grid_height = QSpinBox(); self.spin_grid_height.setRange(5, 500); self.spin_grid_height.setValue(default_h)
        custom_size_sublayout.addWidget(self.spin_grid_height); custom_size_sublayout.addStretch() 
        size_controls_layout.addLayout(custom_size_sublayout, 1, 1, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft) 
        self.combo_grid_type = QComboBox(); self.combo_grid_type.addItems(["Square", "Peyote/Brick"]); self.combo_grid_type.setCurrentText(initial_grid_type)
        size_controls_layout.addWidget(self.combo_grid_type, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter) 
        self.spin_cell_size = QSpinBox(); self.spin_cell_size.setRange(5, 50); self.spin_cell_size.setValue(initial_cell_size)
        size_controls_layout.addWidget(self.spin_cell_size, 1, 3, alignment=Qt.AlignmentFlag.AlignVCenter) 
        size_controls_layout.setColumnStretch(4, 1) 
        size_section_layout.addWidget(size_label); size_section_layout.addLayout(size_controls_layout)
        
        right_layout.addWidget(design_section_frame, 1); right_layout.addWidget(size_section_frame) 
        main_layout.addWidget(left_panel); main_layout.addWidget(right_panel, 1) 

        # --- Create Actions for Undo/Redo ---
        self._create_actions()

        # --- Connect Signals and Slots ---
        self.btn_load_image.clicked.connect(self.load_image)
        for picker in self.image_pickers: picker.colorPicked.connect(self.palette_widget.add_color) 
        self.palette_widget.colorSelected.connect(self.set_current_color)
        self.btn_clear_grid.clicked.connect(self.grid_canvas.clear_grid) 
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load.clicked.connect(self.load_design)
        self.btn_export_png.clicked.connect(self.export_as_png)
        self.btn_preview.clicked.connect(self.show_preview)
        
        self.combo_presets.currentIndexChanged.connect(self.apply_preset_size) 
        self.spin_cell_size.valueChanged.connect(self.update_grid_size_from_controls) 
        self.combo_grid_type.currentTextChanged.connect(self.update_grid_size_from_controls)
        self.spin_grid_width.valueChanged.connect(self.mark_custom_preset); self.spin_grid_width.valueChanged.connect(self.update_grid_size_from_controls) 
        self.spin_grid_height.valueChanged.connect(self.mark_custom_preset); self.spin_grid_height.valueChanged.connect(self.update_grid_size_from_controls) 
        self.btn_undo.clicked.connect(self.grid_canvas.undo)
        self.btn_redo.clicked.connect(self.grid_canvas.redo)
        self.grid_canvas.undo_redo_changed.connect(self.update_undo_redo_buttons)
        
        self.paint_tool_group.buttonToggled.connect(self._on_paint_tool_changed)
        # MODIFICADO: Conectar el slot con su botón respectivo
        self.btn_tool_sym_v.toggled.connect(self._on_symmetry_v_toggled) 
        self.btn_tool_sym_h.toggled.connect(self._on_symmetry_h_toggled)
        
    def _create_actions(self):
        # ... (código sin cambios)
        self.undo_action = QAction("Undo", self); self.undo_action.setIcon(svg_to_qicon(ICON_UNDO)); self.undo_action.setShortcut(QKeySequence.StandardKey.Undo) 
        self.undo_action.setEnabled(False); self.undo_action.triggered.connect(self.grid_canvas.undo); self.addAction(self.undo_action) 
        self.redo_action = QAction("Redo", self); self.redo_action.setIcon(svg_to_qicon(ICON_REDO)); self.redo_action.setShortcuts([QKeySequence.StandardKey.Redo, QKeySequence("Ctrl+Shift+Z")]) 
        self.redo_action.setEnabled(False); self.redo_action.triggered.connect(self.grid_canvas.redo); self.addAction(self.redo_action)
        
    def update_undo_redo_buttons(self, can_undo: bool, can_redo: bool):
        # ... (código sin cambios)
        self.btn_undo.setEnabled(can_undo); self.btn_redo.setEnabled(can_redo)
        self.undo_action.setEnabled(can_undo); self.redo_action.setEnabled(can_redo)

    def _on_paint_tool_changed(self, button: QPushButton, checked: bool):
        """Slot to handle paint *tool* selection (Pencil, Fill, etc.)."""
        if not checked: return 
        tool_id = self.paint_tool_group.id(button)
        if tool_id == 0: # Pencil
            # self.grid_canvas.current_tool = "pencil" # Para el futuro
            pass
        # (Aquí se añadirían otras herramientas, como el bote de pintura)
            
    # --- NUEVOS Slots para simetría, actualizando icono y estado del lienzo ---
    def _on_symmetry_v_toggled(self, checked: bool):
        """Handles vertical symmetry button toggle."""
        self.grid_canvas.mirror_mode_vertical = checked
        color = ICON_COLOR_ACTIVE if checked else ICON_COLOR_INACTIVE
        self.btn_tool_sym_v.setIcon(svg_to_qicon(ICON_SYMMETRY_VERTICAL_DESCRIPTIVE, color))
        self.grid_canvas.update()

    def _on_symmetry_h_toggled(self, checked: bool):
        """Handles horizontal symmetry button toggle."""
        self.grid_canvas.mirror_mode_horizontal = checked
        color = ICON_COLOR_ACTIVE if checked else ICON_COLOR_INACTIVE
        self.btn_tool_sym_h.setIcon(svg_to_qicon(ICON_SYMMETRY_HORIZONTAL_DESCRIPTIVE, color))
        self.grid_canvas.update()

    # --- Slots de Cargar/Guardar (Actualizados para usar los nuevos botones de simetría) ---
    def load_image(self):
        # ... (código sin cambios)
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Inspiration Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_path: return
        original_image = QImage(file_path);
        if original_image.isNull(): print(f"Error: Failed to load image file: {file_path}"); return
        crop_dialog = CropDialog(original_image, self) 
        if crop_dialog.exec() == QDialog.DialogCode.Accepted:
            cropped_image = crop_dialog.get_cropped_image()
            if cropped_image and not cropped_image.isNull():
                current_picker = self.image_pickers[self.image_load_index]; current_picker.set_image(cropped_image) 
                self.image_load_index = (self.image_load_index + 1) % len(self.image_pickers)
            else: print("Warning: Cropping failed or resulted in an empty image.")

    def update_grid_size_from_controls(self):
        # ... (código sin cambios)
        w = self.spin_grid_width.value(); h = self.spin_grid_height.value()
        current_cell_size = self.spin_cell_size.value(); current_grid_type = self.combo_grid_type.currentText()
        sender = self.sender() 
        if sender in [self.spin_cell_size, self.combo_grid_type, self.spin_grid_width, self.spin_grid_height]: self.mark_custom_preset() 
        current_size = (w, h); preset_match = "Custom"
        for name, size in PRESET_SIZES.items(): 
            if size == current_size and name != "Custom": preset_match = name; break
        if self.combo_presets.currentText() != preset_match:
             self.combo_presets.blockSignals(True); self.combo_presets.setCurrentText(preset_match); self.combo_presets.blockSignals(False)
        self.grid_canvas.set_cell_size(current_cell_size); self.grid_canvas.set_grid_type(current_grid_type); self.grid_canvas.set_grid_size(w, h) 

    def mark_custom_preset(self):
        # ... (código sin cambios)
         sender = self.sender()
         if sender == self.spin_grid_width or sender == self.spin_grid_height:
            if self.combo_presets.currentText() != "Custom": self.combo_presets.blockSignals(True); self.combo_presets.setCurrentText("Custom"); self.combo_presets.blockSignals(False)

    def apply_preset_size(self):
        # ... (código sin cambios)
        preset_name = self.combo_presets.currentText();
        if preset_name == "Custom": return 
        w, h = PRESET_SIZES.get(preset_name, (0, 0)) 
        self.spin_grid_width.blockSignals(True); self.spin_grid_height.blockSignals(True)
        self.spin_grid_width.setValue(w); self.spin_grid_height.setValue(h)
        self.spin_grid_width.blockSignals(False); self.spin_grid_height.blockSignals(False)
        self.update_grid_size_from_controls() 

    def set_current_color(self, color: QColor):
        # ... (código sin cambios)
        self.grid_canvas.set_current_color(color)
        if color.alpha() == 0: self.current_color_swatch.setStyleSheet("border: 1px dashed #f8d7da; background-color: #4f2222;")
        else: self.current_color_swatch.setStyleSheet(f"border: 1px solid #999; background-color: {color.name()};")

    def show_preview(self):
        # ... (código sin cambios)
        self.grid_canvas.update(); QApplication.processEvents() 
        pixmap = self.grid_canvas.grab() 
        if pixmap.isNull(): print("Error: Failed to grab canvas pixmap for preview."); return
        dialog = PreviewDialog(pixmap, self); dialog.exec() 

    def save_design(self):
        """Saves the current design, including the *correct* symmetry states."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Design", "", "Design Files (*.json)")
        if not file_path: return 
        if not file_path.lower().endswith(".json"): file_path += ".json"
        
        design_data = {
            "metadata": {"app": "BeadworkDesigner", "version": self.version},
            "palette": self.palette_widget.get_palette_data(), 
            "grid_size": {"width": self.grid_canvas.grid_width, "height": self.grid_canvas.grid_height},
            "cell_size": self.grid_canvas.cell_size, "grid_type": self.grid_canvas.grid_type,
            # --- MODIFICADO: Guardar el estado de los *nuevos* botones de simetría ---
            "mirror_mode_horizontal": self.btn_tool_sym_h.isChecked(), 
            "mirror_mode_vertical": self.btn_tool_sym_v.isChecked(),
            "grid_data": self.grid_canvas.get_grid_data() 
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(design_data, f, indent=2) 
        except Exception as e: print(f"Error saving file '{file_path}': {e}")

    def load_design(self):
        """Loads a design and updates the symmetry buttons."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Design", "", "Design Files (*.json)")
        if not file_path: return 
        try:
            with open(file_path, 'r', encoding='utf-8') as f: design_data = json.load(f)
            self.palette_widget.load_palette(design_data.get("palette", []))
            loaded_grid_type = design_data.get("grid_type", "Square"); self.combo_grid_type.blockSignals(True)
            self.combo_grid_type.setCurrentText(loaded_grid_type); self.combo_grid_type.blockSignals(False)
            self.grid_canvas.set_grid_type(loaded_grid_type) 
            loaded_cell_size = design_data.get("cell_size", 12); self.spin_cell_size.setValue(loaded_cell_size)
            self.grid_canvas.set_cell_size(loaded_cell_size) 
            grid_data = design_data.get("grid_data", [])
            loaded_successfully = False
            if grid_data:
                saved_w = design_data.get("grid_size", {}).get("width", self.grid_canvas.grid_width)
                saved_h = design_data.get("grid_size", {}).get("height", self.grid_canvas.grid_height)
                self.spin_grid_width.blockSignals(True); self.spin_grid_height.blockSignals(True)
                self.spin_grid_width.setValue(saved_w); self.spin_grid_height.setValue(saved_h)
                self.spin_grid_height.blockSignals(False) # Desbloquear antes de llamar a setChecked que dispara signals
                self.spin_grid_width.blockSignals(False)
                loaded_successfully = self.grid_canvas.load_grid_data(grid_data) 
            else: 
                saved_w = design_data.get("grid_size", {}).get("width", self.grid_canvas.grid_width)
                saved_h = design_data.get("grid_size", {}).get("height", self.grid_canvas.grid_height)
                self.spin_grid_width.setValue(saved_w); self.spin_grid_height.setValue(saved_h)
                self.grid_canvas.set_grid_size(saved_w, saved_h); loaded_successfully = True 

            if loaded_successfully: 
                 loaded_size = (self.grid_canvas.grid_width, self.grid_canvas.grid_height)
                 preset_match = "Custom"
                 for name, size in PRESET_SIZES.items():
                     if size == loaded_size and name != "Custom": preset_match = name; break
                 self.combo_presets.blockSignals(True); self.combo_presets.setCurrentText(preset_match); self.combo_presets.blockSignals(False)
            
            # --- MODIFICADO: Cargar el estado de los nuevos botones de simetría ---
            mirror_h_state = design_data.get("mirror_mode_horizontal", False)
            mirror_v_state = design_data.get("mirror_mode_vertical", False)
            
            # Establecer el estado de los botones (esto activará los slots _on_symmetry_..._toggled)
            self.btn_tool_sym_h.setChecked(mirror_h_state)
            self.btn_tool_sym_v.setChecked(mirror_v_state)
            
            # Asegurarse de que el botón de lápiz esté activo si no hay otras herramientas
            self.btn_tool_pencil.setChecked(True)
            # --- Fin Modificación ---
                
            self.grid_canvas._update_canvas_size_hint()
            # Ya no se necesita grid_canvas.update() aquí, los slots de simetría lo hacen
        except FileNotFoundError: print(f"Error: File not found '{file_path}'")
        except json.JSONDecodeError: print(f"Error: Could not decode JSON from '{file_path}'")
        except Exception as e: print(f"An unexpected error occurred while loading file '{file_path}': {e}")

    def export_as_png(self):
        # ... (código sin cambios) ...
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Images (*.png)")
        if not file_path: return 
        if not file_path.lower().endswith(".png"): file_path += ".png"
        original_zoom = self.grid_canvas.zoom_factor; original_pan = self.grid_canvas.pan_offset
        try:
            base_width_multiplier = self.grid_canvas.grid_width + 0.5 if self.grid_canvas.grid_type == "Peyote/Brick" else self.grid_canvas.grid_width
            unzoomed_width = int(base_width_multiplier * self.grid_canvas.cell_size) + 1 
            unzoomed_height = int(self.grid_canvas.grid_height * self.grid_canvas.cell_size) + 1
            pixmap = QPixmap(unzoomed_width, unzoomed_height)
            if pixmap.isNull(): print("Error: Failed to create pixmap for export (possibly too large)."); return
            pixmap.fill(QColor("#e0e0e0")) 
            painter = QPainter(pixmap)
            if not painter.isActive(): print("Error: Failed to create QPainter for export."); painter.end(); return
            self.grid_canvas.zoom_factor = 1.0; self.grid_canvas.pan_offset = QPointF(0.0, 0.0)
            self.grid_canvas.render(painter, QPoint(), flags=QWidget.RenderFlag.DrawChildren) 
            painter.end() 
            if not pixmap.save(file_path, "PNG"): print(f"Error: Failed to save PNG file to '{file_path}'")
        except Exception as e:
            print(f"An unexpected error occurred during PNG export: {e}")
            if 'painter' in locals() and painter.isActive(): painter.end() 
        finally:
            self.grid_canvas.zoom_factor = original_zoom; self.grid_canvas.pan_offset = original_pan
            self.grid_canvas._update_canvas_size_hint(); self.grid_canvas.update()

# --- Fin de la clase MainWindow ---