# widgets/image_picker.py (v8.1 - Force Square Fill)

# --- Imports needed specifically for this widget ---
from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame 
from PyQt6.QtGui import QPixmap, QImage, QColor, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QPoint 

class ImageColorPicker(QLabel):
    """
    A QLabel that displays a square inspiration image, allows color picking,
    and dynamically resizes while maintaining a square aspect ratio.
    """
    colorPicked = pyqtSignal(QColor)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_image: QImage | None = None
        
        # Policy allows expanding/contracting
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        self.setMinimumSize(100, 100) # Reasonable minimum size
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFrameShape(QFrame.Shape.StyledPanel) # Use the imported QFrame
        self.setText("Load an image here")
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setObjectName("ImagePicker") # For styling

    def hasHeightForWidth(self) -> bool:
        """Indicates that height depends on width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Returns the preferred height for a given width (makes it square)."""
        return width

    def sizeHint(self) -> QSize:
        """Provides a reasonable preferred initial size."""
        return QSize(160, 160) 

    def set_image(self, image: QImage):
        """Sets the widget's image from a QImage object (expects a square image)."""
        if image.isNull(): 
            self.setText("Error loading image")
            self.original_image = None
            self.setStyleSheet("") # Reset stylesheet
            self.updateGeometry()
            self.setPixmap(QPixmap()) # Clear pixmap
            return
        
        # Assume the incoming image from CropDialog is already square
        self.original_image = image.convertToFormat(QImage.Format.Format_ARGB32)
        
        # Update pixmap immediately
        self._updatePixmap() 

        # Update appearance and notify layout
        self.setText("")
        self.setStyleSheet("#ImagePicker { border: 1px solid #3c3c3c; background-color: #2b2b2b; }") 
        self.updateGeometry() 

    def _updatePixmap(self):
        """Helper function to scale the square image to fill the widget."""
        if self.original_image and not self.original_image.isNull() and self.size().isValid():
            # --- CHANGE v8.1 ---
            # Scale the image to the exact widget size. Since both are square,
            # IgnoreAspectRatio will fill it perfectly without distortion.
            pixmap = QPixmap.fromImage(self.original_image).scaled(
                self.size(), 
                Qt.AspectRatioMode.IgnoreAspectRatio, # Force fill square widget
                Qt.TransformationMode.SmoothTransformation 
            )
            self.setPixmap(pixmap)
        else:
             self.setPixmap(QPixmap()) # Clear if no valid image

    def resizeEvent(self, event: QEvent | None = None): 
        """Redraws the scaled pixmap when the layout resizes the widget."""
        # The base class resizeEvent needs to be called
        if event:
             super().resizeEvent(event) 
        # Update the pixmap to fit the new size
        self._updatePixmap() 
        
    def mousePressEvent(self, event: QMouseEvent): 
        """Emits the selected color on click."""
        if self.original_image and event.button() == Qt.MouseButton.LeftButton:
            pixmap = self.pixmap()
            # Ensure pixmap exists and is valid before proceeding
            if not pixmap or pixmap.isNull(): return
            
            click_pos = event.position() 
            img_x = click_pos.x() 
            img_y = click_pos.y()

            # Check click is within widget bounds (redundant but safe)
            if not (0 <= img_x < self.width() and 0 <= img_y < self.height()): return

            # Pixmap should fill the widget now, so scaling is direct
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            if pixmap_width == 0 or pixmap_height == 0: return # Avoid division by zero

            # Scale click position to original image coordinates
            original_x = int(img_x * (self.original_image.width() / pixmap_width)) 
            original_y = int(img_y * (self.original_image.height() / pixmap_height))
            
            # Clamp coordinates to be within the original image bounds
            original_x = max(0, min(original_x, self.original_image.width() - 1)) 
            original_y = max(0, min(original_y, self.original_image.height() - 1))
            
            # Get and emit the color if it's not transparent
            color = self.original_image.pixelColor(original_x, original_y)
            if color.alpha() == 0: return 
            self.colorPicked.emit(color)
            
        # Call base class event handler
        super().mousePressEvent(event)

# --- Fin de la clase ImageColorPicker ---