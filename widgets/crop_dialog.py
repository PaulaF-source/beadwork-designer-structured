# widgets/crop_dialog.py

# --- Imports needed specifically for this dialog ---
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QRubberBand, QSizePolicy
)
from PyQt6.QtGui import QImage, QPixmap, QMouseEvent, QResizeEvent # Added QResizeEvent
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QEvent # Added QEvent

# --- CropDialog class definition goes below ---
class CropDialog(QDialog):
    """
    A dialog that displays an image and allows the user to select
    a SQUARE crop area using a rubber band. Returns the cropped QImage.
    """
    def __init__(self, original_image: QImage, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Inspiration Square")
        self.setMinimumSize(600, 600) # Minimum dialog size

        if original_image.isNull():
            raise ValueError("CropDialog requires a valid QImage.") # Fail early if image is invalid

        self.original_image: QImage = original_image
        self.original_pixmap: QPixmap = QPixmap.fromImage(self.original_image)
        self.scaled_pixmap: QPixmap | None = None # Will hold the currently displayed pixmap

        self.origin_point: QPoint = QPoint() # Start point for rubber band drag
        self.selection_rect: QRect = QRect() # Current selection rectangle in widget coords

        # --- Layout ---
        layout = QVBoxLayout(self)

        self.instructions = QLabel("Click and drag to select a square area.")
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instructions)

        # --- Image Label (central widget) ---
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400) # Minimum label size
        # Allow label to expand within the dialog
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        layout.addWidget(self.image_label, 1) # The '1' makes it expandable

        # --- RubberBand for selection (child of image_label) ---
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.image_label)

        # --- Dialog Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept) # Connect signals
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # --- Styling (can be moved to QSS later if preferred) ---
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; }
            QLabel { background-color: #1a1a1a; border: 1px solid #3c3c3c; color: #f0f0f0; }
            QPushButton { background-color: #495057; color: #f8f9fa; border: none; padding: 10px 15px; border-radius: 5px; font-weight: bold; min-width: 80px; }
            QPushButton:hover { background-color: #5a6268; }
            QPushButton:pressed { background-color: #343a40; }
        """)

        # Trigger initial resize to scale pixmap
        self.resize(self.minimumSizeHint()) 

    def resizeEvent(self, event: QResizeEvent | None = None): # Use QResizeEvent type hint
        """Scales the pixmap to fit the label when the dialog is resized."""
        super().resizeEvent(event) if event else None # Call base implementation

        if not self.image_label.size().isValid(): return # Avoid scaling if size is invalid

        # Scale original_pixmap to fit the current image_label size
        self.scaled_pixmap = self.original_pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(self.scaled_pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        """Starts the rubber band selection when the left mouse button is pressed."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Map global dialog coordinates to local image_label coordinates
            widget_pos = self.image_label.mapFrom(self, event.pos())

            # Start selection only if click is inside the image_label bounds
            if self.image_label.rect().contains(widget_pos):
                self.origin_point = widget_pos
                # Start rubber band at the click point with zero size
                self.rubber_band.setGeometry(QRect(self.origin_point, QSize()))
                self.rubber_band.show()
            else:
                 self.origin_point = QPoint() # Ensure origin is reset if clicked outside

    def mouseMoveEvent(self, event: QMouseEvent):
        """Resizes the rubber band during drag, enforcing a square shape."""
        # Only resize if dragging started (origin_point is not null)
        if not self.origin_point.isNull():
            widget_pos = self.image_label.mapFrom(self, event.pos())

            # Calculate vector from origin to current position
            delta_x = widget_pos.x() - self.origin_point.x()
            delta_y = widget_pos.y() - self.origin_point.y()

            # Determine the side length of the square (max of absolute delta values)
            size = max(abs(delta_x), abs(delta_y))

            # Calculate the final square rectangle, maintaining origin
            # Use sign of delta to determine direction from origin
            final_rect = QRect(
                self.origin_point.x(),
                self.origin_point.y(),
                size if delta_x >= 0 else -size, # Width depends on direction
                size if delta_y >= 0 else -size  # Height depends on direction
            ).normalized() # Ensure width/height are positive

            # Keep selection within the bounds of the image label
            bounded_rect = final_rect.intersected(self.image_label.rect()) 

            self.selection_rect = bounded_rect # Store the current selection
            self.rubber_band.setGeometry(self.selection_rect) # Update rubber band geometry

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Finalizes the rubber band selection."""
        if event.button() == Qt.MouseButton.LeftButton and not self.origin_point.isNull():
            # Optional: could add validation here if selection is too small
            if self.selection_rect.width() < 10 or self.selection_rect.height() < 10:
                 self.rubber_band.hide() # Hide if too small
                 self.selection_rect = QRect() # Reset selection

            self.origin_point = QPoint() # Reset origin to indicate dragging finished

    def get_cropped_image(self) -> QImage | None:
        """
        Calculates the crop area corresponding to the selection_rect 
        on the original image and returns the cropped QImage.
        Returns None if selection is invalid or cropping fails.
        """
        # Check if selection is valid and we have the necessary pixmap
        if self.selection_rect.isNull() or not self.scaled_pixmap or self.scaled_pixmap.isNull():
            print("Warning: Invalid selection or pixmap for cropping.")
            return None

        selection_in_widget = self.selection_rect

        # --- Map selection coordinates from widget space to original image space ---

        # 1. Calculate offsets (letterboxing) of the scaled pixmap within the image label
        offset_x = (self.image_label.width() - self.scaled_pixmap.width()) / 2
        offset_y = (self.image_label.height() - self.scaled_pixmap.height()) / 2

        # 2. Adjust selection to be relative to the scaled pixmap (remove offsets)
        pixmap_x = selection_in_widget.x() - offset_x
        pixmap_y = selection_in_widget.y() - offset_y

        # 3. Calculate scaling factors (original size / displayed size)
        # Avoid division by zero if pixmap is somehow invalid
        pixmap_width = self.scaled_pixmap.width()
        pixmap_height = self.scaled_pixmap.height()
        if pixmap_width == 0 or pixmap_height == 0: 
            print("Error: Scaled pixmap has zero dimensions.")
            return None

        scale_x = self.original_image.width() / pixmap_width
        scale_y = self.original_image.height() / pixmap_height

        # 4. Scale the selection rectangle coordinates to the original image
        original_x = int(pixmap_x * scale_x)
        original_y = int(pixmap_y * scale_y)
        original_w = int(selection_in_widget.width() * scale_x)
        original_h = int(selection_in_widget.height() * scale_y)

        # 5. Create the crop rectangle in original image coordinates
        # Ensure the rectangle stays within the original image bounds
        crop_rect = QRect(original_x, original_y, original_w, original_h)
        final_crop_rect = crop_rect.intersected(self.original_image.rect())

        if final_crop_rect.isEmpty():
             print("Warning: Calculated crop area is outside the original image bounds.")
             return None

        # 6. Perform the crop on the *original* image and return the result
        return self.original_image.copy(final_crop_rect)

# --- Fin de la clase CropDialog ---