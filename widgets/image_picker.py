# widgets/image_picker.py

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame
from PyQt6.QtGui import QPixmap, QImage, QColor, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QPoint # Import base QEvent, QPoint

# --- The ImageColorPicker class definition goes below ---
class ImageColorPicker(QLabel):
    colorPicked = pyqtSignal(QColor)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_image = None
        
        # Policy allows expanding/contracting
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        self.setMinimumSize(100, 100) 
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFrameShape(QFrame.Shape.StyledPanel) # QFrame needed here? No, it's inherited.
        self.setText("Load an image here")
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setObjectName("ImagePicker")

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return width

    def sizeHint(self):
        return QSize(160, 160) 

    def set_image(self, image: QImage):
        """Sets the widget's image from a QImage object."""
        # Add docstring for clarity
        if image.isNull(): 
            self.setText("Error loading image"); self.original_image = None; self.setStyleSheet(""); self.updateGeometry(); self.setPixmap(QPixmap()); return
        
        self.original_image = image.convertToFormat(QImage.Format.Format_ARGB32)
        
        self._updatePixmap() 

        self.setText(""); self.setStyleSheet("#ImagePicker { border: 1px solid #3c3c3c; background-color: #2b2b2b; }"); 
        self.updateGeometry() 

    def _updatePixmap(self):
        """Helper function to scale and set the pixmap."""
        if self.original_image and not self.original_image.isNull() and self.size().isValid():
            pixmap = QPixmap.fromImage(self.original_image).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(pixmap)
        else:
             self.setPixmap(QPixmap()) 

    def resizeEvent(self, event: QEvent | None): # Add type hint for event
        """Redraws the scaled pixmap when the widget size changes."""
        # Check if event is not None before passing
        if event:
             super().resizeEvent(event) 
        self._updatePixmap() 

    def mousePressEvent(self, event: QMouseEvent): # Add type hint for event
        """Emits the selected color on click."""
        if self.original_image and event.button() == Qt.MouseButton.LeftButton:
            pixmap = self.pixmap();
            if not pixmap or pixmap.isNull(): return
            
            click_pos = event.position(); 
            
            offset_x = (self.width() - pixmap.width()) / 2
            offset_y = (self.height() - pixmap.height()) / 2
            
            img_x = click_pos.x() - offset_x
            img_y = click_pos.y() - offset_y

            if not (0 <= img_x < pixmap.width() and 0 <= img_y < pixmap.height()): return

            # Defensive check for division by zero if pixmap is tiny
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            if pixmap_width == 0 or pixmap_height == 0: return

            original_x = int(img_x * (self.original_image.width() / pixmap_width)); 
            original_y = int(img_y * (self.original_image.height() / pixmap_height))
            
            original_x = max(0, min(original_x, self.original_image.width() - 1)); 
            original_y = max(0, min(original_y, self.original_image.height() - 1))
            
            color = self.original_image.pixelColor(original_x, original_y)
            if color.alpha() == 0: return
            self.colorPicked.emit(color)
        super().mousePressEvent(event)