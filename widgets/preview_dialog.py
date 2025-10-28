# widgets/preview_dialog.py

# --- Imports needed specifically for this dialog ---
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# --- PreviewDialog class definition goes below ---
class PreviewDialog(QDialog):
    """
    A simple dialog to display a preview pixmap, scaled for better viewing.
    """
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Design Preview")

        if pixmap.isNull():
             print("Warning: PreviewDialog received an invalid pixmap.")
             # Optionally set a default size or show an error message

        layout = QVBoxLayout(self)
        self.preview_label = QLabel()

        # Scale preview slightly larger for better viewing in the dialog
        # Define max preview dimensions
        MAX_PREVIEW_WIDTH = 800
        MAX_PREVIEW_HEIGHT = 600
        scaled_pixmap = pixmap.scaled(
            MAX_PREVIEW_WIDTH, 
            MAX_PREVIEW_HEIGHT, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview_label.setPixmap(scaled_pixmap)
        layout.addWidget(self.preview_label)

        # Standard OK button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept) # Close dialog on OK
        layout.addWidget(button_box)

        # Apply basic dark theme styling
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; }
            QLabel { background-color: #1a1a1a; border: 1px solid #3c3c3c; }
            QPushButton { 
                background-color: #495057; color: #f8f9fa; border: none; 
                padding: 10px 15px; border-radius: 5px; font-weight: bold; 
                min-width: 80px; 
            }
            QPushButton:hover { background-color: #5a6268; }
            QPushButton:pressed { background-color: #343a40; }
        """)

        # Adjust dialog size based on the scaled pixmap + margins
        # Add some padding around the image and for the button
        extra_width = 40 
        extra_height = 80 
        self.resize(scaled_pixmap.width() + extra_width, scaled_pixmap.height() + extra_height)

# --- Fin de la clase PreviewDialog ---