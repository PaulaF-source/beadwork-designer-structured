# main_window.py (v8.0 - No functional changes needed for basic Zoom/Pan)

import sys 
import json

# --- Qt Modules ---
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QFrame, QSizePolicy, QComboBox,
    QScrollArea, QCheckBox, QApplication, QDialog 
)
from PyQt6.QtGui import QIcon, QColor, QImage 
from PyQt6.QtCore import Qt, QSize, pyqtSignal 

# --- Import Widgets from 'widgets' package ---
from widgets.image_picker import ImageColorPicker
from widgets.palette_widget import PaletteWidget
from widgets.grid_canvas import GridCanvas # GridCanvas v8.0 imported
from widgets.crop_dialog import CropDialog
from widgets.preview_dialog import PreviewDialog

# --- Import Utilities from 'utils' package ---
from utils.helpers import (
    svg_to_qicon, 
    ICON_SAVE, ICON_LOAD, ICON_EXPORT, ICON_CLEAR, ICON_PREVIEW 
)
from utils.constants import PRESET_SIZES, DEFAULT_PRESET_NAME

# --- MainWindow class definition ---
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.version = "8.0" # Version bump
        self.setWindowTitle(f"Beadwork Designer v{self.version}") 
        self.image_load_index = 0 
        
        # --- Main Widget and Layout ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Panel ---
        # ... (Left panel layout code unchanged from v7.3) ...
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(570) 
        left_panel.setObjectName("LeftPanel")
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        inspiration_frame = QFrame()
        inspiration_frame.setObjectName("SectionFrame")
        inspiration_layout = QVBoxLayout(inspiration_frame)
        inspiration_layout.setContentsMargins(10, 10, 10, 10)
        load_section_label = QLabel("Inspiration")
        load_section_label.setObjectName("SectionHeader")
        inspiration_layout.addWidget(load_section_label)
        self.btn_load_image = QPushButton() 
        self.btn_load_image.setIcon(svg_to_qicon(ICON_LOAD)) 
        self.btn_load_image.setIconSize(QSize(24, 24)) 
        self.btn_load_image.setToolTip("Load Inspiration Image") 
        self.btn_load_image.setObjectName("PrimaryButton") 
        inspiration_layout.addWidget(self.btn_load_image)
        image_grid_container = QWidget()
        image_grid = QGridLayout(image_grid_container)
        image_grid_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.image_pickers = [ImageColorPicker() for _ in range(4)] 
        image_grid.addWidget(self.image_pickers[0], 0, 0)
        image_grid.addWidget(self.image_pickers[1], 0, 1)
        image_grid.addWidget(self.image_pickers[2], 1, 0)
        image_grid.addWidget(self.image_pickers[3], 1, 1)
        image_grid.setHorizontalSpacing(10)
        image_grid.setVerticalSpacing(10)
        image_grid.setContentsMargins(0, 5, 0, 0)
        image_grid.setColumnStretch(0, 1)
        image_grid.setColumnStretch(1, 1)
        image_grid.setRowStretch(0, 1)
        image_grid.setRowStretch(1, 1)
        inspiration_layout.addWidget(image_grid_container)
        palette_section_frame = QFrame()
        palette_section_frame.setObjectName("SectionFrame")
        palette_section_layout = QVBoxLayout(palette_section_frame)
        palette_section_layout.setContentsMargins(10, 10, 10, 10)
        palette_label = QLabel("Color Palette")
        palette_label.setObjectName("SectionHeader")
        self.palette_widget = PaletteWidget() 
        self.current_color_label = QLabel("Selected:") 
        self.current_color_swatch = QLabel()
        self.current_color_swatch.setFixedSize(30, 30)
        self.current_color_swatch.setStyleSheet("border: 1px solid #555; background-color: #2c2c2c;") 
        current_color_layout = QHBoxLayout()
        current_color_layout.addWidget(self.current_color_label)
        current_color_layout.addWidget(self.current_color_swatch)
        current_color_layout.addStretch()
        palette_section_layout.addWidget(palette_label)
        palette_section_layout.addWidget(self.palette_widget)
        palette_section_layout.addLayout(current_color_layout)
        left_layout.addWidget(inspiration_frame)
        left_layout.addWidget(palette_section_frame)
        left_layout.addStretch() 

        # --- Right Panel ---
        # ... (Right panel layout code unchanged from v7.3) ...
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)
        design_section_frame = QFrame()
        design_section_frame.setObjectName("SectionFrame")
        design_section_layout = QVBoxLayout(design_section_frame)
        design_section_layout.setContentsMargins(10, 10, 10, 10)
        design_header_layout = QHBoxLayout()
        design_label = QLabel("Design Canvas")
        design_label.setObjectName("SectionHeader")
        design_header_layout.addWidget(design_label)
        design_header_layout.addStretch() 
        self.check_mirror_mode_vertical = QCheckBox("Vertical")
        self.check_mirror_mode_vertical.setToolTip("Enable Vertical Mirror Mode")
        design_header_layout.addWidget(self.check_mirror_mode_vertical)
        self.check_mirror_mode_horizontal = QCheckBox("Horizontal")
        self.check_mirror_mode_horizontal.setToolTip("Enable Horizontal Mirror Mode")
        design_header_layout.addWidget(self.check_mirror_mode_horizontal)
        design_section_layout.addLayout(design_header_layout)
        self.canvas_scroll_area = QScrollArea()
        self.canvas_scroll_area.setWidgetResizable(True)
        self.canvas_scroll_area.setObjectName("CanvasScrollArea")
        self.canvas_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.grid_canvas = GridCanvas() # Creates the NEW GridCanvas v8.0
        default_w, default_h = PRESET_SIZES[DEFAULT_PRESET_NAME]
        initial_grid_type = "Square" 
        initial_cell_size = 12 
        self.grid_canvas.set_grid_type(initial_grid_type)
        self.grid_canvas.set_cell_size(initial_cell_size)
        self.grid_canvas.set_grid_size(default_w, default_h) 
        self.canvas_scroll_area.setWidget(self.grid_canvas)
        io_controls_layout = QHBoxLayout()
        self.btn_preview = QPushButton()
        self.btn_preview.setIcon(svg_to_qicon(ICON_PREVIEW))
        self.btn_preview.setToolTip("Preview Design")
        self.btn_save = QPushButton()
        self.btn_save.setIcon(svg_to_qicon(ICON_SAVE))
        self.btn_save.setToolTip("Save Design")
        self.btn_load = QPushButton()
        self.btn_load.setIcon(svg_to_qicon(ICON_LOAD))
        self.btn_load.setToolTip("Load Design")
        self.btn_export_png = QPushButton()
        self.btn_export_png.setIcon(svg_to_qicon(ICON_EXPORT))
        self.btn_export_png.setToolTip("Export as PNG")
        self.btn_clear_grid = QPushButton()
        self.btn_clear_grid.setIcon(svg_to_qicon(ICON_CLEAR, color="#f8d7da")) 
        self.btn_clear_grid.setObjectName("DangerButton") 
        self.btn_clear_grid.setToolTip("Clear Grid")
        io_controls_layout.addWidget(self.btn_preview)
        io_controls_layout.addWidget(self.btn_save)
        io_controls_layout.addWidget(self.btn_load)
        io_controls_layout.addWidget(self.btn_export_png)
        io_controls_layout.addStretch() 
        io_controls_layout.addWidget(self.btn_clear_grid)
        design_section_layout.addWidget(self.canvas_scroll_area, 1) 
        design_section_layout.addLayout(io_controls_layout)
        size_section_frame = QFrame()
        size_section_frame.setObjectName("SectionFrame")
        size_section_layout = QVBoxLayout(size_section_frame)
        size_section_layout.setContentsMargins(10, 10, 10, 10)
        size_label = QLabel("Canvas Size & Resolution")
        size_label.setObjectName("SectionHeader")
        size_controls_layout = QGridLayout() 
        size_controls_layout.setHorizontalSpacing(15) 
        size_controls_layout.addWidget(QLabel("Presets:"), 0, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Custom Grid Size:"), 0, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Grid Type:"), 0, 2, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight) 
        size_controls_layout.addWidget(QLabel("Cell Size (px):"), 0, 3, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(PRESET_SIZES.keys()) 
        self.combo_presets.setCurrentText(DEFAULT_PRESET_NAME)
        size_controls_layout.addWidget(self.combo_presets, 1, 0, alignment=Qt.AlignmentFlag.AlignVCenter) 
        custom_size_sublayout = QHBoxLayout()
        custom_size_sublayout.setContentsMargins(0, 0, 0, 0) 
        custom_size_sublayout.setSpacing(5) 
        custom_size_sublayout.addWidget(QLabel("Cols:"))
        self.spin_grid_width = QSpinBox()
        self.spin_grid_width.setRange(5, 500)
        self.spin_grid_width.setValue(default_w)
        custom_size_sublayout.addWidget(self.spin_grid_width)
        custom_size_sublayout.addSpacing(15) 
        custom_size_sublayout.addWidget(QLabel("Rows:"))
        self.spin_grid_height = QSpinBox()
        self.spin_grid_height.setRange(5, 500)
        self.spin_grid_height.setValue(default_h)
        custom_size_sublayout.addWidget(self.spin_grid_height)
        custom_size_sublayout.addStretch() 
        size_controls_layout.addLayout(custom_size_sublayout, 1, 1, alignment=Qt.AlignmentFlag.AlignVCenter) 
        self.combo_grid_type = QComboBox()
        self.combo_grid_type.addItems(["Square", "Peyote/Brick"])
        self.combo_grid_type.setCurrentText(initial_grid_type)
        size_controls_layout.addWidget(self.combo_grid_type, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter) 
        self.spin_cell_size = QSpinBox()
        self.spin_cell_size.setRange(5, 50)
        self.spin_cell_size.setValue(initial_cell_size)
        size_controls_layout.addWidget(self.spin_cell_size, 1, 3, alignment=Qt.AlignmentFlag.AlignVCenter) 
        size_controls_layout.setColumnStretch(4, 1) 
        size_section_layout.addWidget(size_label)
        size_section_layout.addLayout(size_controls_layout)
        right_layout.addWidget(design_section_frame, 1) 
        right_layout.addWidget(size_section_frame) 
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1) 

        # --- Connect Signals and Slots (Unchanged from v7.3) ---
        self.btn_load_image.clicked.connect(self.load_image)
        for picker in self.image_pickers:
            picker.colorPicked.connect(self.palette_widget.add_color) 
        self.palette_widget.colorSelected.connect(self.set_current_color)
        self.btn_clear_grid.clicked.connect(self.grid_canvas.clear_grid)
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load.clicked.connect(self.load_design)
        self.btn_export_png.clicked.connect(self.export_as_png)
        self.btn_preview.clicked.connect(self.show_preview)
        self.check_mirror_mode_horizontal.stateChanged.connect(self.grid_canvas.set_mirror_mode_horizontal)
        self.check_mirror_mode_vertical.stateChanged.connect(self.grid_canvas.set_mirror_mode_vertical)
        self.combo_presets.currentIndexChanged.connect(self.apply_preset_size) 
        self.spin_cell_size.valueChanged.connect(self.update_grid_size_from_controls) 
        self.combo_grid_type.currentTextChanged.connect(self.update_grid_size_from_controls)
        self.spin_grid_width.valueChanged.connect(self.mark_custom_preset)
        self.spin_grid_width.valueChanged.connect(self.update_grid_size_from_controls) 
        self.spin_grid_height.valueChanged.connect(self.mark_custom_preset)
        self.spin_grid_height.valueChanged.connect(self.update_grid_size_from_controls) 

    # --- Slot Functions (Unchanged from v7.3) ---
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Inspiration Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_path: return
        original_image = QImage(file_path)
        if original_image.isNull():
            print(f"Error: Failed to load image file: {file_path}")
            return
        crop_dialog = CropDialog(original_image, self) 
        if crop_dialog.exec() == QDialog.DialogCode.Accepted:
            cropped_image = crop_dialog.get_cropped_image()
            if cropped_image and not cropped_image.isNull():
                current_picker = self.image_pickers[self.image_load_index]
                current_picker.set_image(cropped_image) 
                self.image_load_index = (self.image_load_index + 1) % len(self.image_pickers)
            else: print("Warning: Cropping failed or resulted in an empty image.")

    def update_grid_size_from_controls(self):
        w = self.spin_grid_width.value(); h = self.spin_grid_height.value()
        current_cell_size = self.spin_cell_size.value(); current_grid_type = self.combo_grid_type.currentText()
        sender = self.sender() 
        if sender in [self.spin_cell_size, self.combo_grid_type, self.spin_grid_width, self.spin_grid_height]:
             self.mark_custom_preset() 
        current_size = (w, h); preset_match = "Custom"
        for name, size in PRESET_SIZES.items(): 
            if size == current_size and name != "Custom": preset_match = name; break
        if self.combo_presets.currentText() != preset_match:
             self.combo_presets.blockSignals(True); self.combo_presets.setCurrentText(preset_match); self.combo_presets.blockSignals(False)
        self.grid_canvas.set_cell_size(current_cell_size)
        self.grid_canvas.set_grid_type(current_grid_type)
        self.grid_canvas.set_grid_size(w, h) 

    def mark_custom_preset(self):
         sender = self.sender()
         if sender == self.spin_grid_width or sender == self.spin_grid_height:
            if self.combo_presets.currentText() != "Custom":
                self.combo_presets.blockSignals(True); self.combo_presets.setCurrentText("Custom"); self.combo_presets.blockSignals(False)

    def apply_preset_size(self):
        preset_name = self.combo_presets.currentText()
        if preset_name == "Custom": return 
        w, h = PRESET_SIZES.get(preset_name, (0, 0)) 
        self.spin_grid_width.blockSignals(True); self.spin_grid_height.blockSignals(True)
        self.spin_grid_width.setValue(w); self.spin_grid_height.setValue(h)
        self.spin_grid_width.blockSignals(False); self.spin_grid_height.blockSignals(False)
        self.update_grid_size_from_controls() 

    def set_current_color(self, color: QColor):
        self.grid_canvas.set_current_color(color)
        if color.alpha() == 0: self.current_color_swatch.setStyleSheet("border: 1px dashed #f8d7da; background-color: #4f2222;")
        else: self.current_color_swatch.setStyleSheet(f"border: 1px solid #999; background-color: {color.name()};")

    def show_preview(self):
        self.grid_canvas.update(); QApplication.processEvents() 
        pixmap = self.grid_canvas.grab() 
        if pixmap.isNull(): print("Error: Failed to grab canvas pixmap for preview."); return
        dialog = PreviewDialog(pixmap, self); dialog.exec() 

    def save_design(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Design", "", "Design Files (*.json)")
        if not file_path: return 
        if not file_path.lower().endswith(".json"): file_path += ".json"
        design_data = {
            "metadata": {"app": "BeadworkDesigner", "version": self.version},
            "palette": self.palette_widget.get_palette_data(), 
            "grid_size": {"width": self.grid_canvas.grid_width, "height": self.grid_canvas.grid_height},
            "cell_size": self.grid_canvas.cell_size, "grid_type": self.grid_canvas.grid_type,
            "mirror_mode_horizontal": self.check_mirror_mode_horizontal.isChecked(), 
            "mirror_mode_vertical": self.check_mirror_mode_vertical.isChecked(),
            # --- Save Zoom/Pan state? ---
            # "view_state": {
            #     "zoom": self.grid_canvas.zoom_factor,
            #     "pan_x": self.grid_canvas.pan_offset.x(),
            #     "pan_y": self.grid_canvas.pan_offset.y()
            # },
            "grid_data": self.grid_canvas.get_grid_data() 
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(design_data, f, indent=2) 
        except Exception as e: print(f"Error saving file '{file_path}': {e}")

    def load_design(self):
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
                self.spin_grid_width.blockSignals(False); self.spin_grid_height.blockSignals(False)
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
            mirror_h_state = design_data.get("mirror_mode_horizontal", False)
            self.check_mirror_mode_horizontal.setChecked(mirror_h_state)
            self.grid_canvas.mirror_mode_horizontal = mirror_h_state 
            mirror_v_state = design_data.get("mirror_mode_vertical", False)
            self.check_mirror_mode_vertical.setChecked(mirror_v_state)
            self.grid_canvas.mirror_mode_vertical = mirror_v_state
            
            # --- Load Zoom/Pan state? ---
            # view_state = design_data.get("view_state")
            # if view_state:
            #      self.grid_canvas.zoom_factor = view_state.get("zoom", 1.0)
            #      self.grid_canvas.pan_offset = QPointF(view_state.get("pan_x", 0.0), view_state.get("pan_y", 0.0))
            # else: # Reset if not saved
            #      self.grid_canvas.zoom_factor = 1.0
            #      self.grid_canvas.pan_offset = QPointF(0.0, 0.0)

            self.grid_canvas._update_canvas_size_hint() # Update size hint after potential zoom/pan/size change
            self.grid_canvas.update() 
        except FileNotFoundError: print(f"Error: File not found '{file_path}'")
        except json.JSONDecodeError: print(f"Error: Could not decode JSON from '{file_path}'")
        except Exception as e: print(f"An unexpected error occurred while loading file '{file_path}': {e}")

    def export_as_png(self):
        """Exports the current GridCanvas content as a PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Images (*.png)")
        if not file_path: return 
        if not file_path.lower().endswith(".png"): file_path += ".png"
        
        # --- Exporting zoomed/panned view vs full grid ---
        # Option 1: Export EXACTLY what's visible (including zoom/pan)
        # self.grid_canvas.update(); QApplication.processEvents() 
        # pixmap = self.grid_canvas.grab() 

        # Option 2: Export the FULL grid at 100% zoom (More common for patterns)
        # Create a pixmap of the correct unzoomed size and render onto it
        base_width_multiplier = self.grid_canvas.grid_width + 0.5 if self.grid_canvas.grid_type == "Peyote/Brick" else self.grid_canvas.grid_width
        unzoomed_width = int(base_width_multiplier * self.grid_canvas.cell_size) + 1 
        unzoomed_height = int(self.grid_canvas.grid_height * self.grid_canvas.cell_size) + 1
        pixmap = QPixmap(unzoomed_width, unzoomed_height)
        pixmap.fill(Qt.GlobalColor.transparent) # Or QColor("#e0e0e0") if you want background
        
        painter = QPainter(pixmap)
        # Temporarily reset zoom/pan for rendering the full grid
        original_zoom = self.grid_canvas.zoom_factor
        original_pan = self.grid_canvas.pan_offset
        self.grid_canvas.zoom_factor = 1.0
        self.grid_canvas.pan_offset = QPointF(0.0, 0.0)
        
        # Ask the canvas to render itself onto the painter/pixmap
        # The paintEvent logic needs to respect the painter passed to it
        self.grid_canvas.render(painter, QPoint(), renderFlags=QWidget.RenderFlag.DrawChildren) # Might need adjustments
        
        # Restore original zoom/pan
        self.grid_canvas.zoom_factor = original_zoom
        self.grid_canvas.pan_offset = original_pan
        painter.end()
        # --- End Option 2 ---

        if pixmap.isNull():
             print("Error: Failed to create pixmap for export.")
             return
        if not pixmap.save(file_path, "PNG"):
             print(f"Error: Failed to save PNG file to '{file_path}'")

# --- Fin de la clase MainWindow ---