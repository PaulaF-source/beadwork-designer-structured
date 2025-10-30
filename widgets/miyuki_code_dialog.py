# widgets/miyuki_code_dialog.py (v9.5 - Modo Edición para Acabados)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox, 
    QMessageBox, QFrame, QPushButton, QColorDialog, QComboBox, QWidget
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QSize, QPointF

# Importamos el catálogo y el modelo que creamos
from models import BeadColorEntry
from utils.miyuki_catalog import get_miyuki_data 

# --- CONSTANTE: Acabados Comunes para Selección Manual ---
COMMON_FINISHES = [
    "Opaque (Custom)", 
    "Metallic (Custom)", 
    "Luster (Custom)", 
    "Transparent (Custom)", 
    "Matte (Custom)",
    "Opaque (Image Pick)" # Asegurarse de que el valor por defecto esté
]


class MiyukiCodeDialog(QDialog):
    
    MIYUKI_PREFIX = "DB" 

    def __init__(self, existing_entry: BeadColorEntry | None = None, parent=None):
        super().__init__(parent)
        
        # Guardar la entrada existente si se está editando
        self.result_entry: BeadColorEntry | None = existing_entry
        self.is_edit_mode = (existing_entry is not None)
        
        if self.is_edit_mode:
            self.setWindowTitle("Edit Bead Finish")
            # Usar el color de la entrada existente
            self.current_preview_color = existing_entry.color
            # En modo edición, el color manual siempre está "seleccionado"
            self.manual_color_selected = True 
        else:
            self.setWindowTitle("Select Miyuki Color Code")
            self.current_preview_color = QColor("#404040") 
            self.manual_color_selected = False

        self.setFixedSize(450, 350) 
        
        # --- Layout Principal ---
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # --- 1. Contenedor de Búsqueda de Código (Solo visible en modo 'Añadir') ---
        self.search_widget = QWidget()
        input_layout = QHBoxLayout(self.search_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter Miyuki Code Number (e.g., 1832)")
        self.code_input.setFont(QFont("Monospace", 10))
        self.code_input.textChanged.connect(self._update_preview) 
        self.code_input.editingFinished.connect(self._search_code) 
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self._search_code)
        
        input_layout.addWidget(QLabel(self.MIYUKI_PREFIX)) 
        input_layout.addWidget(self.code_input, 1)
        input_layout.addWidget(self.btn_search)
        layout.addWidget(self.search_widget)

        # --- 2. Contenedor para el selector de acabado manual ---
        self.manual_finish_widget = QWidget()
        self.manual_finish_layout = QHBoxLayout(self.manual_finish_widget)
        self.manual_finish_layout.setContentsMargins(0, 0, 0, 0)
        self.manual_finish_layout.addWidget(QLabel("Finish:"))
        self.finish_selector = QComboBox()
        self.finish_selector.addItems(COMMON_FINISHES)
        self.finish_selector.currentTextChanged.connect(self._apply_manual_finish)
        self.manual_finish_layout.addWidget(self.finish_selector, 1)
        
        self.manual_finish_widget.setVisible(False) # Oculto hasta que se edite o falle la búsqueda
        layout.addWidget(self.manual_finish_widget)
        
        # --- 3. Vista Previa del Color y Metadata ---
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setFixedSize(QSize(400, 95)) 
        
        metadata_layout = QVBoxLayout(self.preview_frame)
        metadata_layout.setSpacing(2) 
        metadata_layout.setContentsMargins(10, 5, 10, 5) 

        self.lbl_name = QLabel("Name: N/A")
        self.lbl_finish = QLabel("Finish: N/A")
        self.lbl_code_display = QLabel("Code: N/A")
        
        self.lbl_name.setMinimumHeight(18)
        self.lbl_finish.setMinimumHeight(18)
        self.lbl_code_display.setMinimumHeight(18)
        
        metadata_layout.addWidget(self.lbl_name)
        metadata_layout.addWidget(self.lbl_finish)
        metadata_layout.addWidget(self.lbl_code_display)
        
        layout.addWidget(self.preview_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- 4. Fallback y Botones de Diálogo ---
        
        self.btn_fallback = QPushButton("Or Select Custom Color...")
        self.btn_fallback.clicked.connect(self._open_color_dialog_fallback)
        layout.addWidget(self.btn_fallback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False) 
        button_box.accepted.connect(self.accept) 
        button_box.rejected.connect(self.reject)
        self.button_box = button_box
        
        layout.addWidget(self.button_box)
        
        # --- LÓGICA DE INICIALIZACIÓN (Modo Edición vs Añadir) ---
        if self.is_edit_mode:
            # Configurar para Modo Edición
            self.search_widget.setVisible(False) # Ocultar búsqueda de código
            self.btn_fallback.setVisible(False) # Ocultar botón de fallback
            self.manual_finish_widget.setVisible(True) # Mostrar selector de acabado
            
            # Asegurarse de que el acabado actual esté en la lista
            current_finish = existing_entry.finish
            if current_finish not in COMMON_FINISHES:
                self.finish_selector.addItem(current_finish)
                
            self.finish_selector.setCurrentText(current_finish)
            
            # Poblar la preview (usando _apply_manual_finish)
            self._apply_manual_finish(current_finish)
            
            # Habilitar OK
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            # Configurar para Modo Añadir (por defecto)
            self._update_preview(self.code_input.text())

        
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #f0f0f0; }
            QLineEdit { background-color: #1a1a1a; border: 1px solid #444; color: #f8f9fa; padding: 5px; }
            QLabel { color: #f0f0f0; }
            QFrame { border-radius: 5px; }
            QPushButton { min-height: 25px; } 
        """)
        
    def _apply_manual_finish(self, finish_text: str):
        """
        Actualiza el BeadColorEntry resultante y la vista previa 
        con el acabado seleccionado manualmente.
        """
        if self.manual_color_selected:
            # Crear/Actualizar el BeadColorEntry
            self.result_entry = BeadColorEntry(
                color=self.current_preview_color, 
                finish=finish_text, 
                code=self.result_entry.code if self.is_edit_mode else None, # Conservar código si se edita
                name=self.current_preview_color.name().upper()
            )
            
            self.lbl_name.setText(f"Name: {self.result_entry.name}")
            self.lbl_finish.setText(f"Finish: {self.result_entry.finish}")
            self.lbl_code_display.setText(f"Code: {self.result_entry.code or 'Custom'}")

            self._draw_preview_style(self.result_entry)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)


    def _draw_preview_style(self, entry: BeadColorEntry):
        """Función auxiliar para dibujar el estilo de la preview (incluye brillo)."""
        if entry.is_shiny():
            self.preview_frame.setStyleSheet(
                f"background-color: qradialgradient(cx: 0.3, cy: 0.3, radius: 1, fx: 0.3, fy: 0.3, stop: 0 #FFFFFF, stop: 0.2 {entry.color.lighter(150).name()}, stop: 1.0 {entry.color.darker(110).name()}); border: 2px solid #FFFFFF;"
            )
        else:
            self.preview_frame.setStyleSheet(
                f"background-color: {entry.color.name()}; border: 1px solid #555;"
            )
            
    def _get_full_code(self, raw_input: str) -> str:
        """Asegura que el código tenga el formato DBxxxx."""
        normalized = raw_input.upper().replace(" ", "").strip()
        if normalized.startswith(self.MIYUKI_PREFIX):
            return normalized
        elif normalized and normalized.isdigit():
            return self.MIYUKI_PREFIX + normalized
        return normalized

    def _update_preview(self, code: str):
        """Lógica de búsqueda principal para códigos Miyuki."""
        # Este método solo se usa en modo 'Añadir'
        if self.is_edit_mode:
            return 
            
        full_code = self._get_full_code(code)
        data = get_miyuki_data(full_code)
        
        self.manual_finish_widget.setVisible(False)
        self.manual_color_selected = False
        code_found = False
        
        if data:
            # Código Miyuki encontrado
            color = QColor(data["hex"])
            self.current_preview_color = color
            entry = BeadColorEntry(color, finish=data["finish"], code=full_code, name=data["name"])
            
            self.lbl_name.setText(f"Name: {data['name']}")
            self.lbl_finish.setText(f"Finish: {data['finish']}")
            self.lbl_code_display.setText(f"Code: {full_code}")
            self.result_entry = entry
            code_found = True
            self._draw_preview_style(entry)
            
        else:
            # Código Miyuki NO encontrado
            self.current_preview_color = QColor("#404040")
            self.lbl_name.setText("Name: Code not found!")
            self.lbl_finish.setText("Finish: N/A")
            self.lbl_code_display.setText(f"Code: {full_code or 'N/A'}")
            self.result_entry = None
            
            if code:
                 self.preview_frame.setStyleSheet(f"background-color: {self.current_preview_color.name()}; border: 1px dashed red;")
            else:
                 self.preview_frame.setStyleSheet(f"background-color: {self.current_preview_color.name()}; border: 1px solid #555;")
        
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(code_found)


    def _search_code(self):
        """Fuerza la actualización de la preview al presionar 'Search' o finalizar edición."""
        if self.is_edit_mode:
            return # No buscar en modo edición
            
        code = self.code_input.text()
        self._update_preview(code)
        
        if not self.result_entry and code:
             QMessageBox.warning(self, "Code Not Found", 
                                 f"Miyuki code '{self._get_full_code(code)}' was not found in the catalog.")


    def _open_color_dialog_fallback(self):
        """
        Abre el QColorDialog. Si se acepta, muestra el selector de acabado manual 
        en el MiyukiCodeDialog principal.
        """
        initial_color = self.current_preview_color if self.current_preview_color.isValid() else QColor.fromRgb(0, 0, 0)
        color_dialog = QColorDialog(initial_color, self)
        
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_color = color_dialog.selectedColor()
            
            if selected_color.isValid():
                self.current_preview_color = selected_color
                self.manual_color_selected = True
                
                self.search_widget.setVisible(False) # Ocultar búsqueda
                self.btn_fallback.setVisible(False)
                
                self.manual_finish_widget.setVisible(True)
                
                # Forzar la creación de la entrada y el redibujado
                self._apply_manual_finish(self.finish_selector.currentText()) 
        
    def get_bead_entry(self) -> BeadColorEntry | None:
        """Retorna la BeadColorEntry si el diálogo se acepta."""
        return self.result_entry