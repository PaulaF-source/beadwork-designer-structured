# main_window.py

import sys # Needed if standalone, but maybe not if main.py handles QApplication
import json

# --- Qt Modules ---
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QFrame, QSizePolicy, QComboBox,
    QScrollArea, QCheckBox, QApplication, 
    QDialog # <-- AÑADIR ESTO
)
from PyQt6.QtGui import QIcon, QColor, QImage # QIcon for icons, QColor, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal # QSize for icons, Qt flags, pyqtSignal potentially if needed later

# --- Import Widgets from 'widgets' package ---
from widgets.image_picker import ImageColorPicker
from widgets.palette_widget import PaletteWidget
from widgets.grid_canvas import GridCanvas
from widgets.crop_dialog import CropDialog
from widgets.preview_dialog import PreviewDialog

# --- Import Utilities from 'utils' package ---
from utils.helpers import (
    svg_to_qicon, 
    ICON_SAVE, ICON_LOAD, ICON_EXPORT, ICON_CLEAR, ICON_APPLY, ICON_PREVIEW
)
from utils.constants import PRESET_SIZES, DEFAULT_PRESET_NAME

# --- MainWindow class definition goes below ---
class MainWindow(QMainWindow):
    # --- Make sure PRESET_SIZES and DEFAULT_PRESET_NAME are accessible ---
    # No need to redefine them here, they are imported from constants
    # PRESET_SIZES = PRESET_SIZES # Already imported
    # DEFAULT_PRESET_NAME = DEFAULT_PRESET_NAME # Already imported

    def __init__(self):
        super().__init__()
        # Use f-string for versioning if you plan to update it
        self.version = "7.2" # Example version
        self.setWindowTitle(f"Beadwork Designer v{self.version}") 

        self.image_load_index = 0 # Tracks which ImageColorPicker gets the next image

        # --- Main Widget and Layout ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Panel ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        # Use a reasonable fixed width or make it resizable later
        left_panel.setFixedWidth(570) 
        left_panel.setObjectName("LeftPanel") # For styling
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # --- Section 1: Inspiration ---
        inspiration_frame = QFrame()
        inspiration_frame.setObjectName("SectionFrame")
        inspiration_layout = QVBoxLayout(inspiration_frame)
        inspiration_layout.setContentsMargins(10, 10, 10, 10) # Padding inside the frame

        load_section_label = QLabel("Inspiration")
        load_section_label.setObjectName("SectionHeader")
        inspiration_layout.addWidget(load_section_label)

        # Load Image Button (using icon)
        self.btn_load_image = QPushButton() # Text removed
        self.btn_load_image.setIcon(svg_to_qicon(ICON_LOAD)) 
        self.btn_load_image.setIconSize(QSize(24, 24)) # Adjust size as needed
        self.btn_load_image.setToolTip("Load Inspiration Image") 
        self.btn_load_image.setObjectName("PrimaryButton") # Style as primary action
        inspiration_layout.addWidget(self.btn_load_image)

        # Image Picker Grid Container
        image_grid_container = QWidget()
        image_grid = QGridLayout(image_grid_container)
        image_grid_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Create ImageColorPicker instances (imported class)
        self.image_pickers = [ImageColorPicker() for _ in range(4)] 

        # Add pickers to the grid
        image_grid.addWidget(self.image_pickers[0], 0, 0)
        image_grid.addWidget(self.image_pickers[1], 0, 1)
        image_grid.addWidget(self.image_pickers[2], 1, 0)
        image_grid.addWidget(self.image_pickers[3], 1, 1)

        image_grid.setHorizontalSpacing(10)
        image_grid.setVerticalSpacing(10)
        image_grid.setContentsMargins(0, 5, 0, 0) # Top margin after button

        # Ensure columns and rows stretch equally (important for square pickers)
        image_grid.setColumnStretch(0, 1)
        image_grid.setColumnStretch(1, 1)
        image_grid.setRowStretch(0, 1)
        image_grid.setRowStretch(1, 1)

        inspiration_layout.addWidget(image_grid_container)

        # --- Section 2: Color Palette ---
        palette_section_frame = QFrame()
        palette_section_frame.setObjectName("SectionFrame")
        palette_section_layout = QVBoxLayout(palette_section_frame)
        palette_section_layout.setContentsMargins(10, 10, 10, 10)

        palette_label = QLabel("Color Palette")
        palette_label.setObjectName("SectionHeader")

        # Create PaletteWidget instance (imported class)
        self.palette_widget = PaletteWidget() 

        # Selected Color Swatch
        self.current_color_label = QLabel("Selected:") # Shortened label
        self.current_color_swatch = QLabel()
        self.current_color_swatch.setFixedSize(30, 30)
        # Default style for swatch (will be updated by set_current_color)
        self.current_color_swatch.setStyleSheet("border: 1px solid #555; background-color: #2c2c2c;") 

        current_color_layout = QHBoxLayout()
        current_color_layout.addWidget(self.current_color_label)
        current_color_layout.addWidget(self.current_color_swatch)
        current_color_layout.addStretch()

        palette_section_layout.addWidget(palette_label)
        palette_section_layout.addWidget(self.palette_widget)
        palette_section_layout.addLayout(current_color_layout)

        # Add sections to left panel layout
        left_layout.addWidget(inspiration_frame)
        left_layout.addWidget(palette_section_frame)
        left_layout.addStretch() # Pushes content to the top

        # --- Right Panel ---
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)

        # --- Section 3: Design Canvas ---
        design_section_frame = QFrame()
        design_section_frame.setObjectName("SectionFrame")
        design_section_layout = QVBoxLayout(design_section_frame)
        design_section_layout.setContentsMargins(10, 10, 10, 10)

        # Design Header with Mirror Checkboxes
        design_header_layout = QHBoxLayout()
        design_label = QLabel("Design Canvas")
        design_label.setObjectName("SectionHeader")
        design_header_layout.addWidget(design_label)
        design_header_layout.addStretch() # Push checkboxes right

        # Mirror Mode Checkboxes
        self.check_mirror_mode_vertical = QCheckBox("Vertical")
        self.check_mirror_mode_vertical.setToolTip("Enable Vertical Mirror Mode")
        design_header_layout.addWidget(self.check_mirror_mode_vertical)

        self.check_mirror_mode_horizontal = QCheckBox("Horizontal")
        self.check_mirror_mode_horizontal.setToolTip("Enable Horizontal Mirror Mode")
        design_header_layout.addWidget(self.check_mirror_mode_horizontal)

        design_section_layout.addLayout(design_header_layout) # Add header layout

        # Scroll Area for Canvas
        self.canvas_scroll_area = QScrollArea()
        self.canvas_scroll_area.setWidgetResizable(True)
        self.canvas_scroll_area.setObjectName("CanvasScrollArea")
        self.canvas_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center canvas if smaller

        # Create GridCanvas instance (imported class)
        self.grid_canvas = GridCanvas() 
        # Get default size from constants
        default_w, default_h = PRESET_SIZES[DEFAULT_PRESET_NAME]
        initial_grid_type = "Square" # Default grid type
        initial_cell_size = 12 # Default cell size
        # Initialize canvas settings
        self.grid_canvas.set_grid_type(initial_grid_type)
        self.grid_canvas.set_cell_size(initial_cell_size)
        self.grid_canvas.set_grid_size(default_w, default_h) 
        # Place canvas inside scroll area
        self.canvas_scroll_area.setWidget(self.grid_canvas)

        # IO Controls (Buttons with Icons)
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
        # Use red color for clear icon
        self.btn_clear_grid.setIcon(svg_to_qicon(ICON_CLEAR, color="#f8d7da")) 
        self.btn_clear_grid.setObjectName("DangerButton") # Style as danger
        self.btn_clear_grid.setToolTip("Clear Grid")

        # Add buttons to layout
        io_controls_layout.addWidget(self.btn_preview)
        io_controls_layout.addWidget(self.btn_save)
        io_controls_layout.addWidget(self.btn_load)
        io_controls_layout.addWidget(self.btn_export_png)
        io_controls_layout.addStretch() # Push clear button right
        io_controls_layout.addWidget(self.btn_clear_grid)

        design_section_layout.addWidget(self.canvas_scroll_area, 1) # Scroll area expands
        design_section_layout.addLayout(io_controls_layout)

        # --- Section 4: Define Size ---
        size_section_frame = QFrame()
        size_section_frame.setObjectName("SectionFrame")
        size_section_layout = QVBoxLayout(size_section_frame)
        size_section_layout.setContentsMargins(10, 10, 10, 10)

        size_label = QLabel("Canvas Size & Resolution")
        size_label.setObjectName("SectionHeader")

        # Use GridLayout for better alignment of size controls
        size_controls_layout = QGridLayout() 

        # Row 0: Labels
        size_controls_layout.addWidget(QLabel("Presets:"), 0, 0, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Custom Grid Size:"), 0, 1, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Grid Type:"), 0, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        size_controls_layout.addWidget(QLabel("Cell Size (px):"), 0, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        # Row 1: Controls
        # Preset ComboBox
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(PRESET_SIZES.keys()) # Use imported constant
        self.combo_presets.setCurrentText(DEFAULT_PRESET_NAME) # Use imported constant
        size_controls_layout.addWidget(self.combo_presets, 1, 0, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Custom Size SpinBoxes (in a sub-layout for compactness)
        custom_size_sublayout = QHBoxLayout()
        custom_size_sublayout.addWidget(QLabel("Cols:"))
        self.spin_grid_width = QSpinBox()
        self.spin_grid_width.setRange(5, 500) # Max columns
        self.spin_grid_width.setValue(default_w) # Set default
        custom_size_sublayout.addWidget(self.spin_grid_width)
        custom_size_sublayout.addWidget(QLabel("Rows:"))
        self.spin_grid_height = QSpinBox()
        self.spin_grid_height.setRange(5, 500) # Max rows
        self.spin_grid_height.setValue(default_h) # Set default
        custom_size_sublayout.addWidget(self.spin_grid_height)
        size_controls_layout.addLayout(custom_size_sublayout, 1, 1, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Grid Type ComboBox
        self.combo_grid_type = QComboBox()
        self.combo_grid_type.addItems(["Square", "Peyote/Brick"])
        self.combo_grid_type.setCurrentText(initial_grid_type)
        size_controls_layout.addWidget(self.combo_grid_type, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Cell Size SpinBox
        self.spin_cell_size = QSpinBox()
        self.spin_cell_size.setRange(5, 50) # Min/Max cell size
        self.spin_cell_size.setValue(initial_cell_size)
        size_controls_layout.addWidget(self.spin_cell_size, 1, 3, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Apply Button (with Icon)
        self.btn_set_grid_size = QPushButton() 
        self.btn_set_grid_size.setIcon(svg_to_qicon(ICON_APPLY))
        self.btn_set_grid_size.setToolTip("Apply Size")
        size_controls_layout.addWidget(self.btn_set_grid_size, 1, 4, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Add stretch to the last column to push controls left
        size_controls_layout.setColumnStretch(5, 1) 

        size_section_layout.addWidget(size_label)
        size_section_layout.addLayout(size_controls_layout)

        # Add sections to right panel layout
        right_layout.addWidget(design_section_frame, 1) # Design section expands vertically
        right_layout.addWidget(size_section_frame) # Size section stays fixed height

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1) # Right panel expands horizontally

        # --- Connect Signals and Slots ---
        # Inspiration Section
        self.btn_load_image.clicked.connect(self.load_image)
        # Connect color picking signal from *each* picker to the palette's add_color slot
        for picker in self.image_pickers:
            picker.colorPicked.connect(self.palette_widget.add_color) 

        # Palette Section
        self.palette_widget.colorSelected.connect(self.set_current_color)

        # Canvas Section
        self.btn_clear_grid.clicked.connect(self.grid_canvas.clear_grid)
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load.clicked.connect(self.load_design)
        self.btn_export_png.clicked.connect(self.export_as_png)
        self.btn_preview.clicked.connect(self.show_preview)
        # Connect mirror checkboxes to GridCanvas slots
        self.check_mirror_mode_horizontal.stateChanged.connect(self.grid_canvas.set_mirror_mode_horizontal)
        self.check_mirror_mode_vertical.stateChanged.connect(self.grid_canvas.set_mirror_mode_vertical)

        # Size Section
        self.btn_set_grid_size.clicked.connect(self.update_grid_size) # Apply button action
        self.combo_presets.currentIndexChanged.connect(self.apply_preset_size) # Preset selection change
        # Connect controls that should immediately update the canvas (or mark as custom)
        self.spin_cell_size.valueChanged.connect(self.update_grid_size_from_controls) 
        self.combo_grid_type.currentTextChanged.connect(self.update_grid_size_from_controls)
        # Connect dimension spin boxes to mark preset as "Custom" if changed manually
        self.spin_grid_width.valueChanged.connect(self.mark_custom_preset)
        self.spin_grid_height.valueChanged.connect(self.mark_custom_preset)

    # --- Slot Functions (Remain in MainWindow as they coordinate actions) ---

    def load_image(self):
        """Opens file dialog, shows CropDialog, and sets the cropped image."""
        # Consider adding a starting directory or remembering the last directory
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Inspiration Image", 
            "", # Start directory (empty means default/last used)
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return # User cancelled

        original_image = QImage(file_path)
        if original_image.isNull():
            # Maybe show a QMessageBox error here?
            print(f"Error: Failed to load image file: {file_path}")
            return

        # --- Use CropDialog ---
        crop_dialog = CropDialog(original_image, self) # Pass self as parent
        # Use exec() for modal dialog behavior
        if crop_dialog.exec() == QDialog.DialogCode.Accepted:
            cropped_image = crop_dialog.get_cropped_image()

            if cropped_image and not cropped_image.isNull():
                # Find the next available picker
                current_picker = self.image_pickers[self.image_load_index]
                current_picker.set_image(cropped_image) # Pass the QImage object
                # Cycle to the next picker index
                self.image_load_index = (self.image_load_index + 1) % len(self.image_pickers)
            else:
                # Handle case where cropping failed or resulted in empty image
                print("Warning: Cropping failed or resulted in an empty image.")
        # else: User cancelled the CropDialog

    def update_grid_size(self):
        """Applies size/type/cell settings from controls to the GridCanvas."""
        w = self.spin_grid_width.value()
        h = self.spin_grid_height.value()
        current_cell_size = self.spin_cell_size.value()
        current_grid_type = self.combo_grid_type.currentText()

        # Check if current dimensions match a preset (excluding "Custom")
        current_size = (w, h)
        preset_match = "Custom"
        # Iterate through imported PRESET_SIZES
        for name, size in PRESET_SIZES.items(): 
            if size == current_size and name != "Custom":
                preset_match = name
                break

        # Update preset combo silently if necessary
        if self.combo_presets.currentText() != preset_match:
             self.combo_presets.blockSignals(True) # Prevent triggering apply_preset_size again
             self.combo_presets.setCurrentText(preset_match)
             self.combo_presets.blockSignals(False)

        # Apply changes to the canvas widget
        # Order might matter slightly depending on internal logic, but this seems safe:
        self.grid_canvas.set_cell_size(current_cell_size)
        self.grid_canvas.set_grid_type(current_grid_type) 
        self.grid_canvas.set_grid_size(w, h) # This triggers repaint and size hint update

    def update_grid_size_from_controls(self):
        """Slot specifically for Cell Size and Grid Type changes."""
        # This function is called when cell size or grid type combo changes.
        # We want to apply these changes immediately *without* necessarily
        # changing the selected preset away from "Custom".
        w = self.spin_grid_width.value() # Keep current dimensions
        h = self.spin_grid_height.value()
        current_cell_size = self.spin_cell_size.value()
        current_grid_type = self.combo_grid_type.currentText()

        # Mark preset as custom if cell size or type was changed
        # (unless it already matches another preset coincidentally, handled by update_grid_size)
        sender = self.sender() # Get the widget that emitted the signal
        if sender == self.spin_cell_size or sender == self.combo_grid_type:
            self.mark_custom_preset() # Mark as custom if needed

        # Apply changes directly to canvas
        self.grid_canvas.set_cell_size(current_cell_size)
        self.grid_canvas.set_grid_type(current_grid_type)
        # Re-apply dimensions in case grid type change affects geometry (Peyote vs Square)
        self.grid_canvas.set_grid_size(w, h) 

    def mark_custom_preset(self):
         """Sets the preset combobox to 'Custom' if width/height spins are changed."""
         # Check if the signal sender was one of the dimension spin boxes
         sender = self.sender()
         if sender == self.spin_grid_width or sender == self.spin_grid_height:
            # If the current preset is not already "Custom", change it
            if self.combo_presets.currentText() != "Custom":
                self.combo_presets.blockSignals(True) # Avoid recursion
                self.combo_presets.setCurrentText("Custom")
                self.combo_presets.blockSignals(False)


    def apply_preset_size(self):
        """Applies the selected preset's dimensions to the spin boxes and canvas."""
        preset_name = self.combo_presets.currentText()
        if preset_name == "Custom":
             # Do nothing if "Custom" is selected manually
             return 

        # Get dimensions from the imported PRESET_SIZES dictionary
        w, h = PRESET_SIZES.get(preset_name, (0, 0)) # Default to 0,0 if not found

        # Update spin boxes silently (block signals)
        self.spin_grid_width.blockSignals(True)
        self.spin_grid_height.blockSignals(True)
        self.spin_grid_width.setValue(w)
        self.spin_grid_height.setValue(h)
        self.spin_grid_width.blockSignals(False)
        self.spin_grid_height.blockSignals(False)

        # Now, call the main update function to apply everything to the canvas
        self.update_grid_size() 


    def set_current_color(self, color: QColor):
        """Updates the GridCanvas's current color and the color swatch display."""
        self.grid_canvas.set_current_color(color)

        # Update the visual swatch
        if color.alpha() == 0: # Style for eraser
            self.current_color_swatch.setStyleSheet(
                "border: 1px dashed #f8d7da; background-color: #4f2222;"
            )
        else: # Style for regular colors
            self.current_color_swatch.setStyleSheet(
                f"border: 1px solid #999; background-color: {color.name()};"
            )

    def show_preview(self):
        """Shows the PreviewDialog with a snapshot of the current canvas."""
        # Ensure canvas painting is up-to-date
        self.grid_canvas.update() 
        QApplication.processEvents() # Allow Qt to process pending events (like repaint)

        # Grab the canvas content as a QPixmap
        pixmap = self.grid_canvas.grab() 

        if pixmap.isNull():
             print("Error: Failed to grab canvas pixmap for preview.")
             return

        # Create and show the dialog (imported class)
        dialog = PreviewDialog(pixmap, self) 
        dialog.exec() # Use exec() for modal behavior

    def save_design(self):
        """Saves the current design (palette, grid, settings) to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Design", 
            "", # Start directory
            "Design Files (*.json)"
        )
        if not file_path: return # User cancelled

        # Ensure file has .json extension if user didn't type it
        if not file_path.lower().endswith(".json"):
            file_path += ".json"

        # --- Gather data ---
        design_data = {
            "metadata": {"app": "BeadworkDesigner", "version": self.version},
            "palette": self.palette_widget.get_palette_data(), # Get custom colors
            "grid_size": {
                "width": self.grid_canvas.grid_width, 
                "height": self.grid_canvas.grid_height
            },
            "cell_size": self.grid_canvas.cell_size,
            "grid_type": self.grid_canvas.grid_type,
            # Save mirror mode states
            "mirror_mode_horizontal": self.check_mirror_mode_horizontal.isChecked(), 
            "mirror_mode_vertical": self.check_mirror_mode_vertical.isChecked(),
            "grid_data": self.grid_canvas.get_grid_data() # Get cell colors
        }

        # --- Save to JSON ---
        try:
            with open(file_path, 'w', encoding='utf-8') as f: # Use utf-8 encoding
                json.dump(design_data, f, indent=2) # Use indent for readability
        except Exception as e:
             print(f"Error saving file '{file_path}': {e}")
             # Consider showing a QMessageBox error to the user

    def load_design(self):
        """Loads a design from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Design", 
            "", 
            "Design Files (*.json)"
        )
        if not file_path: return # User cancelled

        try:
            with open(file_path, 'r', encoding='utf-8') as f: # Use utf-8 encoding
                design_data = json.load(f)

            # --- Apply loaded data (with defaults for safety) ---

            # Load palette (PaletteWidget handles its own reset)
            self.palette_widget.load_palette(design_data.get("palette", []))

            # Load grid type *before* size/data if possible
            loaded_grid_type = design_data.get("grid_type", "Square") # Default to Square
            self.combo_grid_type.blockSignals(True)
            self.combo_grid_type.setCurrentText(loaded_grid_type)
            self.combo_grid_type.blockSignals(False)
            # Apply type to canvas immediately
            self.grid_canvas.set_grid_type(loaded_grid_type) 

            # Load cell size
            loaded_cell_size = design_data.get("cell_size", 12) # Default to 12px
            self.spin_cell_size.setValue(loaded_cell_size)
            # Apply cell size to canvas immediately
            self.grid_canvas.set_cell_size(loaded_cell_size) 

            # Load grid data and dimensions
            grid_data = design_data.get("grid_data", [])
            if grid_data:
                # Get saved dimensions, fall back to current canvas size if missing
                saved_w = design_data.get("grid_size", {}).get("width", self.grid_canvas.grid_width)
                saved_h = design_data.get("grid_size", {}).get("height", self.grid_canvas.grid_height)

                # Update spin boxes *before* loading grid data, as load_grid_data might update them
                self.spin_grid_width.blockSignals(True)
                self.spin_grid_height.blockSignals(True)
                self.spin_grid_width.setValue(saved_w)
                self.spin_grid_height.setValue(saved_h)
                self.spin_grid_width.blockSignals(False)
                self.spin_grid_height.blockSignals(False)

                # Load the actual cell colors into the canvas
                if self.grid_canvas.load_grid_data(grid_data):
                     # If load was successful, update the preset combo box
                     loaded_size = (self.grid_canvas.grid_width, self.grid_canvas.grid_height)
                     preset_match = "Custom"
                     for name, size in PRESET_SIZES.items():
                         if size == loaded_size and name != "Custom":
                             preset_match = name
                             break
                     self.combo_presets.blockSignals(True)
                     self.combo_presets.setCurrentText(preset_match)
                     self.combo_presets.blockSignals(False)
            else:
                # If no grid_data in file, maybe just set size from "grid_size"?
                saved_w = design_data.get("grid_size", {}).get("width", self.grid_canvas.grid_width)
                saved_h = design_data.get("grid_size", {}).get("height", self.grid_canvas.grid_height)
                self.spin_grid_width.setValue(saved_w)
                self.spin_grid_height.setValue(saved_h)
                self.grid_canvas.set_grid_size(saved_w, saved_h) # Apply empty grid of specified size

            # Load mirror mode states
            mirror_h_state = design_data.get("mirror_mode_horizontal", False)
            self.check_mirror_mode_horizontal.setChecked(mirror_h_state)
            # Ensure canvas internal state matches checkbox
            self.grid_canvas.mirror_mode_horizontal = mirror_h_state 

            mirror_v_state = design_data.get("mirror_mode_vertical", False)
            self.check_mirror_mode_vertical.setChecked(mirror_v_state)
            # Ensure canvas internal state matches checkbox
            self.grid_canvas.mirror_mode_vertical = mirror_v_state

            # Trigger a final update / repaint after loading everything
            self.grid_canvas.update() 
            # self.update_grid_size() # This might reset preset to Custom unnecessarily

        except FileNotFoundError:
             print(f"Error: File not found '{file_path}'")
             # Show QMessageBox error?
        except json.JSONDecodeError:
             print(f"Error: Could not decode JSON from '{file_path}'")
             # Show QMessageBox error?
        except Exception as e: 
             print(f"An unexpected error occurred while loading file '{file_path}': {e}")
             # Show QMessageBox error?

    def export_as_png(self):
        """Exports the current GridCanvas content as a PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export as PNG", 
            "", 
            "PNG Images (*.png)"
        )
        if not file_path: return # User cancelled

        # Ensure extension
        if not file_path.lower().endswith(".png"):
            file_path += ".png"

        # Ensure canvas is up-to-date
        self.grid_canvas.update() 
        QApplication.processEvents() 

        # Grab content and save
        pixmap = self.grid_canvas.grab() 
        if pixmap.isNull():
             print("Error: Failed to grab canvas pixmap for export.")
             return

        if not pixmap.save(file_path, "PNG"):
             print(f"Error: Failed to save PNG file to '{file_path}'")
             # Show QMessageBox error?
        # else: print(f"Successfully exported to {file_path}") # Optional success message

# --- Fin de la clase MainWindow ---